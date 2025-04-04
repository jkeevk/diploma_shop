import pytest
from django.urls import reverse
from rest_framework import status
from django.core import mail
from unittest.mock import patch
from celery import current_app


@pytest.mark.django_db
class TestOrderConfirmation:
    """
    Тестирование подтверждения заказа.
    Проверка успешных сценариев и обработки ошибок при подтверждении корзины.
    """

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """
        Настройка тестового клиента и конфигурации Celery для выполнения задач.
        """
        current_app.conf.task_always_eager = True
        self.client = api_client

    def test_successful_order_confirmation_with_multiple_shops(
        self, customer, order_with_multiple_shops, contact, shops
    ):
        """
        Тест: Успешное подтверждение заказа с несколькими магазинами.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Статус заказа обновлен на 'confirmed'.
        - Отправлено несколько писем:
            - Покупателю: с подтверждением заказа и деталями.
            - Поставщикам: с уведомлением о новом заказе.
        """
        mail.outbox = []

        # Отключаем режим тестирования для отправки реальных писем
        with patch("backend.signals.TESTING", False):
            self.client.force_authenticate(user=customer)
            url = reverse("confirm-basket", args=[contact.id])

            # Отправка запроса на подтверждение заказа
            response = self.client.post(url, format="json")

            # Проверка базового успешного сценария
            assert response.status_code == status.HTTP_200_OK
            assert response.data == {"detail": "Заказ успешно подтвержден."}

            # Обновление и проверка статуса заказа
            order_with_multiple_shops.refresh_from_db()
            assert order_with_multiple_shops.status == "confirmed"

            # Проверка отправленных писем
            assert len(mail.outbox) == 1 + len(
                shops
            ), f"Ожидалось {1 + len(shops)} писем, получено {len(mail.outbox)}"

            # Разделяем письма по типам
            customer_emails = [e for e in mail.outbox if "подтвержден" in e.subject]
            host_emails = [e for e in mail.outbox if "новый заказ" in e.subject]

            # Проверка письма покупателю
            assert len(customer_emails) == 1
            customer_email = customer_emails[0]
            assert customer_email.to == [customer.email]
            assert "Ваш заказ подтвержден" in customer_email.subject
            assert str(order_with_multiple_shops.id) in customer_email.body

            # Проверка содержимого письма покупателю
            for item in order_with_multiple_shops.order_items.all():
                assert item.product.name in customer_email.body
                assert str(item.quantity) in customer_email.body
                assert item.shop.name in customer_email.body

            # Проверка писем поставщикам
            assert len(host_emails) == len(shops)

            # Сортировка магазинов и писем по email для корректного сопоставления
            shops_sorted = sorted(shops, key=lambda s: s.user.email)
            host_emails_sorted = sorted(host_emails, key=lambda e: e.to[0])

            # Проверка содержимого каждого письма с соответствующим магазином
            for shop, email in zip(shops_sorted, host_emails_sorted):
                assert email.to == [
                    shop.user.email
                ], f"Expected {shop.user.email}, got {email.to}"
                assert "Поступил новый заказ" in email.subject
                assert str(order_with_multiple_shops.id) in email.body

            # Проверка контактных данных в письмах
            for email in mail.outbox:
                assert contact.phone in email.body
                assert contact.city in email.body
                assert contact.street in email.body

    def test_empty_basket_confirmation(self, api_client, customer, contact):
        """
        Тест: Ошибка при попытке подтвердить пустую корзину.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке: 'Корзина пуста.'
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket", args=[contact.id])
        response = api_client.post(url, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"non_field_errors": ["Корзина пуста."]}

    def test_invalid_contact_id_confirmation(self, api_client, customer, order):
        """
        Тест: Ошибка при передаче несуществующего contact_id.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке: 'Неверный ID контакта.'
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket", args=[999])
        response = api_client.post(url, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"contact_id": ["Неверный ID контакта."]}

    def test_contact_not_found_error_on_confirmation(
        self, api_client, customer, order, another_user_contact
    ):
        """
        Тест: Ошибка при попытке подтвердить заказ с несуществующим контактным ID.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке: 'Контакт не найден.'
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket", args=[another_user_contact.id])
        response = api_client.post(url, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"contact_id": ["Контакт не найден."]}
