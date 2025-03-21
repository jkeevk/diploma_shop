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

    def test_confirm_basket_empty(self, api_client, customer):
        """
        Проверяем ошибку при попытке подтвердить пустую корзину.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {"contact_id": 1}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Корзина пуста."}

    def test_confirm_basket_missing_contact_id(self, api_client, customer):
        """
        Проверяем ошибку при отсутствии contact_id в запросе.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Корзина пуста."}

    def test_confirm_basket_invalid_contact_id(self, api_client, customer):
        """
        Проверяем ошибку при передаче несуществующего contact_id.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("confirm-basket")
        data = {"contact_id": 999}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Корзина пуста."}
