# Standard library imports
import logging
import re
import subprocess

# Django
from django.conf import settings
from django.core.mail import send_mail
from django.core.management import call_command
from django.urls import reverse

# Celery
from celery import shared_task

# Local imports
from .models import Order, Shop, User

logger = logging.getLogger(__name__)

@shared_task
def export_products_task(file_path: str) -> dict:
    """Асинхронно экспортирует данные о продуктах."""
    try:
        call_command("export_products", file_path)
        return {"message": "Данные успешно загружены"}
    except Exception as e:
        return {"error": str(e)}

@shared_task
def import_products_task() -> dict:
    """Асинхронно импортирует данные о продуктах."""
    try:
        call_command("import_products")
        return {"message": "Данные успешно импортированы"}
    except Exception as e:
        return {"error": str(e)}

@shared_task
def run_pytest() -> dict:
    """
    Асинхронно запускает команду pytest и возвращает результат.
    """
    try:
        logger.info("Запуск pytest...")
        
        result = subprocess.run(
            [
                "pytest",
                "--create-db",
                "--no-migrations",
                "--disable-warnings",
                "--tb=short",
                "-v",
                "backend/tests/"
            ],
            capture_output=True,
            text=True,
        )

        logger.info(f"Результат pytest: {result}")

        output = result.stdout + "\n" + result.stderr
        
        passed = len(re.findall(r'PASSED', output))
        failed = len(re.findall(r'FAILED', output))
        errors = len(re.findall(r'ERROR', output))
        
        failed_tests = re.findall(
            r'(FAILED|ERROR) \[.*?\] (.*?)(?=\n\S+|\Z)', 
            output
        )

        return {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "failed_tests": [f"{res[0]}: {res[1]}" for res in failed_tests],
            "output": output,
        }
    except Exception as e:
        logger.error(f"Ошибка при запуске pytest: {e}", exc_info=True)

@shared_task
def send_confirmation_email_async(user_id: int, token: str) -> None:
    """Асинхронно отправляет письмо для подтверждения регистрации."""
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
def send_email_to_customer_async(recipient_email: str, order_id: int, contact_id: int) -> None:
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

@shared_task
def send_email_to_host_async(recipient_email: str, order_id: int, shop_id: int) -> None:
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
def send_password_reset_email_async(user_id: int, token: str, uid: str) -> None:
    """Асинхронно отправляет письмо для сброса пароля."""
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
