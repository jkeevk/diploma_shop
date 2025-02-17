from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse
from django.db.models.signals import post_save
from django.conf import settings
import uuid
from .models import User

@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:
        token = uuid.uuid4().hex
        instance.confirmation_token = token
        instance.save()

        confirmation_url = reverse("user-register-confirm", kwargs={"token": token})
        full_url = f"{settings.BACKEND_URL}{confirmation_url}"
        subject = "Подтвердите вашу регистрацию"
        message = f"Пожалуйста, перейдите по ссылке, чтобы подтвердить вашу регистрацию: {full_url}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.email])

@receiver(post_save, sender=User)
def send_password_reset_email(sender, instance, **kwargs):
    if hasattr(instance, 'reset_password'):
        token = instance.reset_password['token']
        uid = instance.reset_password['uid']
        reset_link = settings.BACKEND_URL + reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        send_mail(
            subject='Сброс пароля',
            message=f'Пожалуйста, перейдите по ссылке ниже, чтобы сбросить ваш пароль: {reset_link}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.email],
        )
