import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import User


@pytest.mark.django_db
class TestUserRegistration:
    """
    Тесты для регистрации пользователя.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_register_user_without_email_confirmation(self):
        """
        Тест регистрации пользователя без подтверждения email.
        """
        data = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
        }

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.get(email="test@example.com")
        assert user is not None
        assert user.role == "customer"

    def test_register_user_with_wrong_role(self):
        """
        Тест регистрации пользователя с неверной ролью.
        """
        data = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "invalid_role",
        }

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "role" in response.data

    def test_register_user_with_existing_email(self):
        """
        Тест регистрации пользователя с уже существующим email.
        """
        User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            first_name="Test",
            last_name="User",
            role="customer",
        )

        data = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
        }

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_user_without_required_fields(self):
        """
        Тест регистрации пользователя без обязательных полей.
        """
        data = {}

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "password" in response.data
        assert "role" in response.data
