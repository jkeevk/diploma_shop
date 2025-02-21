from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import logging
from .models import User, Order, Shop


logger = logging.getLogger(__name__)

@shared_task
def send_confirmation_email_async(user_id, token):
    """Асинхронно отправляет письмо для подтверждения регистрации пользователя."""
    try:
        user = User.objects.get(id=user_id)
        confirmation_url = reverse("user-register-confirm", kwargs={"token": token})
        full_url = f"{settings.BACKEND_URL}{confirmation_url}"
        subject = "Confirm Your Registration"
        message = (
            f"Please click the link below to confirm your registration: {full_url}"
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        logger.info(f"Confirmation email sent to {user.email} for user ID {user_id}")
    except Exception as e:
        logger.error(f"Failed to send confirmation email to user ID {user_id}: {e}")


@shared_task
def send_password_reset_email_async(user_id, token, uid):
    """Асинхронно отправляет письмо для сброса пароля пользователя."""
    try:
        user = User.objects.get(id=user_id)
        reset_link = settings.BACKEND_URL + reverse(
            "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        send_mail(
            subject="Password Reset",
            message=f"Please click the link below to reset your password: {reset_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        logger.info(f"Password reset email sent to {user.email} for user ID {user_id}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to user ID {user_id}: {e}")


@shared_task
def send_email_to_host_async(recipient_email, order_id, shop_id):
    """Асинхронно отправляет письмо поставщику о новом заказе."""
    try:
        order = Order.objects.get(id=order_id)
        shop = Shop.objects.get(id=shop_id)

        if order.user_id == shop.user_id:
            logger.info(
                f"User {order.user_id} is the owner of shop {shop_id}. Email not sent."
            )
            return

        subject = "Поступил новый заказ"
        message = f"Заказ #{order.id} был подтвержден.\nПодробности:\n"

        for item in order.order_items.filter(shop=shop):
            message += f"Продукт: {item.product.name}\nКоличество: {item.quantity}\n\n"

        contact = order.user.contacts.first()
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
        logger.info(
            f"Email sent to {recipient_email} for order {order_id} and shop {shop_id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to send email to {recipient_email} for order {order_id} and shop {shop_id}: {e}"
        )


@shared_task
def send_email_to_customer_async(recipient_email, order_id, contact_id):
    """Асинхронно отправляет письмо покупателю о подтверждении заказа."""
    try:
        order = Order.objects.get(id=order_id)
        contact = order.user.contacts.get(id=contact_id)
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
        logger.info(
            f"Confirmation email sent to {recipient_email} for order {order_id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to send confirmation email to {recipient_email} for order {order_id}: {e}"
        )
