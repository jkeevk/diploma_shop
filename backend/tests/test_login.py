import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestUserLogin:
    """
    Тесты для авторизации пользователя.
    """

    def test_successful_login(self, api_client, customer):
        """Тест успешной авторизации пользователя."""
        url = reverse("login")
        data = {
            "email": "customer@example.com",
            "password": "strongpassword123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        assert response.data["user_id"] == customer.id
        assert response.data["email"] == customer.email

    def test_invalid_password(self, api_client, customer):
        """Тест авторизации с неправильным паролем."""
        url = reverse("login")
        data = {
            "email": "customer@example.com",
            "password": "wrongpassword123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert response.data["non_field_errors"] == ["Не удалось войти с предоставленными учетными данными."]

    def test_user_not_found(self, api_client):
        """Тест авторизации для несуществующего пользователя."""
        url = reverse("login")
        data = {
            "email": "nonexistent@example.com",
            "password": "strongpassword123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert response.data["non_field_errors"] == ["Не удалось войти с предоставленными учетными данными."]

    def test_inactive_user(self, api_client, supplier):
        """Тест попытки авторизации для неактивного пользователя."""
        url = reverse("login")
        supplier.is_active = False
        supplier.save()

        data = {
            "email": "supplier@example.com",
            "password": "strongpassword123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert response.data["non_field_errors"] == ["Не удалось войти с предоставленными учетными данными."]
