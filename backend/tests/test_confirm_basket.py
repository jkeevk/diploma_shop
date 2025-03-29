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
    """

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        current_app.conf.task_always_eager = True
        self.client = api_client

    def test_confirm_basket_success(
        self, customer, order_with_multiple_shops, contact, shops
    ):
        """
        Проверяем успешное подтверждение заказа.
        Подтверждаем заказ с несколькими магазинами.
        Покупателю и поставщикам отправляется письмо.
        """
        mail.outbox = []
        # Отключаем TESTING режим для этого теста
        with patch("backend.signals.TESTING", False):
            self.client.force_authenticate(user=customer)
            url = reverse("confirm-basket")
            data = {"contact_id": contact.id}

            # Отправляем запрос на подтверждение заказа
            response = self.client.post(url, data, format="json")

            # Проверка базового сценария
            assert response.status_code == status.HTTP_200_OK
            assert response.data == {"detail": "Заказ успешно подтвержден."}

            # Обновляем данные заказа
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

            # Сортируем магазины и письма по email поставщика для корректного сопоставления
            shops_sorted = sorted(shops, key=lambda s: s.user.email)
            host_emails_sorted = sorted(host_emails, key=lambda e: e.to[0])

            # Проверяем каждое письмо с соответствующим магазином
            for shop, email in zip(shops_sorted, host_emails_sorted):
                assert email.to == [
                    shop.user.email
                ], f"Expected {shop.user.email}, got {email.to}"
                assert "Поступил новый заказ" in email.subject
                assert str(order_with_multiple_shops.id) in email.body

            # Проверка контактных данных во всех письмах
            for email in mail.outbox:
                assert contact.phone in email.body
                assert contact.city in email.body
                assert contact.street in email.body

    def test_confirm_basket_empty(self, api_client, customer, contact):
        """
        Проверяем ошибку при попытке подтвердить пустую корзину.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {"contact_id": contact.id}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"non_field_errors": ["Корзина пуста."]}

    def test_confirm_basket_missing_contact_id(self, api_client, customer, order):
        """
        Проверяем ошибку при отсутствии contact_id.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"contact_id": ["ID контакта обязателен."]}

    def test_confirm_basket_invalid_contact_id(self, api_client, customer, order):
        """
        Проверяем ошибку при передаче несуществующего contact_id.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {"contact_id": 999}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"contact_id": ["Неверный ID контакта."]}

    def test_confirm_basket_contact_not_found(
        self, api_client, customer, order, another_user_contact
    ):
        """
        Проверяем ошибку при передаче несуществующего contact_id.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {"contact_id": another_user_contact.id}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"contact_id": ["Контакт не найден."]}
