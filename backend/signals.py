from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import (
    send_confirmation_email_async,
    send_password_reset_email_async,
    send_email_to_host_async,
    send_email_to_customer_async,
)
from .models import User, Order
import uuid


@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    """Отправляет письмо для подтверждения регистрации пользователя."""
    if created and not getattr(instance, "created_by_admin", False):
        token = uuid.uuid4().hex
        instance.confirmation_token = token
        instance.save()

        send_confirmation_email_async.delay(instance.id, token)


@receiver(post_save, sender=User)
def send_password_reset_email(sender, instance, **kwargs):
    """Отправляет письмо для сброса пароля пользователя."""
    if hasattr(instance, "reset_password"):
        token = instance.reset_password["token"]
        uid = instance.reset_password["uid"]

        send_password_reset_email_async.delay(instance.id, token, uid)


@receiver(post_save, sender=Order)
def send_email_to_host(sender, instance, **kwargs):
    """Отправляет письмо поставщику о новом заказе."""
    if instance.status == "confirmed" and not kwargs.get("created"):
        order_items = instance.order_items.all()
        shops = {item.shop for item in order_items}
        for shop in shops:
            if shop and shop.user.email:
                send_email_to_host_async.delay(shop.user.email, instance.id, shop.id)


@receiver(post_save, sender=Order)
def send_email_to_customer(sender, instance, **kwargs):
    """Отправляет письмо покупателю о подтверждении заказа."""
    if instance.status == "confirmed" and not kwargs.get("created"):
        contact = instance.user.contacts.first()
        if contact and instance.user.email:
            send_email_to_customer_async.delay(
                instance.user.email, instance.id, contact.id
            )
