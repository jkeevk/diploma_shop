from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse
from django.db.models.signals import post_save
from django.conf import settings
import uuid
from .models import User, Shop, Order

@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    """Отправляет письмо для подтверждения регистрации пользователя."""
    if created and not getattr(instance, 'created_by_admin', False):
        token = uuid.uuid4().hex
        instance.confirmation_token = token
        instance.save()
        
        confirmation_url = reverse("user-register-confirm", kwargs={"token": token})
        full_url = f"{settings.BACKEND_URL}{confirmation_url}"
        subject = "Confirm Your Registration"
        message = f"Please click the link below to confirm your registration: {full_url}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.email])

@receiver(post_save, sender=User)
def send_password_reset_email(sender, instance, **kwargs):
    """Отправляет письмо для сброса пароля пользователя."""
    if hasattr(instance, 'reset_password'):
        token = instance.reset_password['token']
        uid = instance.reset_password['uid']
        reset_link = settings.BACKEND_URL + reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        send_mail(
            subject='Password Reset',
            message=f'Please click the link below to reset your password: {reset_link}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.email],
        )

@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    """Отправляет письмо для подтверждения заказа."""
    if not created and instance.status == "confirmed":
        shop = Shop.objects.filter(user=instance.user).first()
        if shop:
            host_email = shop.user.email
            send_email_to_host(host_email, instance)
        
        contact = instance.user.contacts.first()
        send_email_to_customer(instance.user.email, instance, contact)

def send_email_to_host(recipient_email, order, contact):
    """Отправляет письмо поставщику о новом заказе."""
    subject = "Поступил новый заказ"
    message = f"Заказ #{order.id} был подтвержден.\nПодробности:\n"
    for item in order.order_items.all():
        message += f"Продукт: {item.product.name}\nМагазин: {item.shop.name}\nКоличество: {item.quantity}\n\n"
    
    if contact:
        message += f"\nКонтактные данные:\n"
        message += f"Город: {contact.city}\n"
        message += f"Улица: {contact.street}\n"
        message += f"Дом: {contact.house}\n"
        message += f"Корпус: {contact.structure}\n"
        message += f"Строение: {contact.building}\n"
        message += f"Квартира: {contact.apartment}\n"
        message += f"Телефон: {contact.phone}\n"
    
    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])

def send_email_to_customer(recipient_email, order, contact):
    """Отправляет письмо покупателю о подтверждении заказа."""
    subject = "Ваш заказ подтвержден"
    message = f"Ваш заказ #{order.id} был подтвержден.\nПодробности:\n"
    for item in order.order_items.all():
        message += f"Продукт: {item.product.name}\nМагазин: {item.shop.name}\nКоличество: {item.quantity}\n\n"
    
    if contact:
        message += f"\nКонтактные данные:\n"
        message += f"Город: {contact.city}\n"
        message += f"Улица: {contact.street}\n"
        message += f"Дом: {contact.house}\n"
        message += f"Корпус: {contact.structure}\n"
        message += f"Строение: {contact.building}\n"
        message += f"Квартира: {contact.apartment}\n"
        message += f"Телефон: {contact.phone}\n"
    
    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])