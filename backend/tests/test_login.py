import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from backend.models import User

@pytest.mark.django_db
class TestUserLogin:
    @pytest.fixture
    def client(self):
        """Фикстура для создания тестового клиента API."""
        return APIClient()

    @pytest.fixture
    def user(self):
        """Фикстура для создания пользователя."""
        return User.objects.create_user(
            email="testuser@example.com",
            password="strongpassword",
            first_name="Test",
            last_name="User"
        )

    def test_successful_login(self, client, user):
        """Тест успешной авторизации пользователя."""
        url = reverse("login")
        data = {
            "email": "testuser@example.com",
            "password": "strongpassword"
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        assert response.data["user_id"] == user.id
        assert response.data["email"] == user.email
