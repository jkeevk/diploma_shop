# Standard library imports
import os
import uuid
from typing import Any

# Django
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Local imports
from .tasks import (
    send_confirmation_email_async,
    send_password_reset_email_async,
    send_email_to_host_async,
    send_email_to_customer_async,
    generate_product_image_thumbnails_async,
    generate_user_avatar_thumbnails_async,
)
from .models import User, Order, ProductInfo


@receiver(post_save, sender=User)
def send_confirmation_email(
    sender: Any, instance: User, created: bool, **kwargs: Any
) -> None:
    """
    Отправляет письмо для подтверждения регистрации пользователя.
    """
    if (
        created
        and not getattr(instance, "created_by_admin", False)
        and not settings.TESTING
    ):
        token = uuid.uuid4().hex
        instance.confirmation_token = token
        instance.save()

        send_confirmation_email_async.delay(instance.id, token)


@receiver(post_save, sender=User)
def send_password_reset_email(sender: Any, instance: User, **kwargs: Any) -> None:
    """
    Отправляет письмо для сброса пароля пользователя.
    """
    if hasattr(instance, "reset_password") and not settings.TESTING:
        token = instance.reset_password["token"]
        uid = instance.reset_password["uid"]

        send_password_reset_email_async.delay(instance.id, token, uid)


@receiver(post_save, sender=Order)
def send_email_to_host(sender: Any, instance: Order, **kwargs: Any) -> None:
    """
    Отправляет письмо поставщику о новом заказе.
    """
    if (
        instance.status == "confirmed"
        and not kwargs.get("created")
        and not settings.TESTING
    ):
        order_items = instance.order_items.all()
        shops = {item.shop for item in order_items}
        for shop in shops:
            send_email_to_host_async.delay(shop.user.email, instance.id, shop.id)


@receiver(post_save, sender=Order)
def send_email_to_customer(sender: Any, instance: Order, **kwargs: Any) -> None:
    """
    Отправляет письмо покупателю о подтверждении заказа.
    """
    if (
        instance.status == "confirmed"
        and not kwargs.get("created")
        and not settings.TESTING
    ):
        contact = instance.user.contacts.first()
        send_email_to_customer_async.delay(instance.user.email, instance.id, contact.id)


@receiver(post_save, sender=ProductInfo)
def process_image(sender, instance, **kwargs):
    """
    Генерирует миниатюры изображения продукта.
    """
    if instance.image and not kwargs.get("raw"):
        generate_product_image_thumbnails_async.delay(instance.id)


@receiver(post_save, sender=User)
def handle_avatar_update(sender, instance, **kwargs):
    """
    Генерирует миниатюры аватара пользователя.
    """
    if instance.avatar:
        generate_user_avatar_thumbnails_async.delay(instance.id)
