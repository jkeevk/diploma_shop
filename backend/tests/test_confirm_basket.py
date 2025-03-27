import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestConfirmBasket:
    def test_confirm_basket_success(self, api_client, customer, order, contact):
        """
        Проверяем успешное подтверждение корзины с валидным contact_id.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {"contact_id": contact.id}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "Заказ успешно подтвержден."}

        order.refresh_from_db()
        assert order.status == "confirmed"

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
