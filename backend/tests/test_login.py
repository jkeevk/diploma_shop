import pytest
from django.urls import reverse
from rest_framework import status
from backend.serializers import LoginSerializer

@pytest.mark.django_db
class TestUserLogin:
    """
    Тесты для авторизации пользователя.
    """

    def test_successful_login(self, api_client, customer_login):
        """Тест успешной авторизации пользователя."""
        url = reverse("login")
        data = {"email": "customer@example.com", "password": "strongpassword123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        assert response.data["user_id"] == customer_login.id
        assert response.data["email"] == customer_login.email

    def test_invalid_password(self, api_client, customer_login):
        """Тест авторизации с неправильным паролем."""
        url = reverse("login")
        data = {"email": "customer@example.com", "password": "wrongpassword123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert response.data["non_field_errors"] == [
            "Не удалось войти с предоставленными учетными данными."
        ]

    def test_user_not_found(self, api_client):
        """Тест авторизации для несуществующего пользователя."""
        url = reverse("login")
        data = {"email": "nonexistent@example.com", "password": "strongpassword123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert response.data["non_field_errors"] == [
            "Не удалось войти с предоставленными учетными данными."
        ]

    def test_inactive_user(self, api_client, customer_login):
        """Тест попытки авторизации для неактивного пользователя."""
        url = reverse("login")
        customer_login.is_active = False
        customer_login.save()

        data = {"email": "supplier@example.com", "password": "strongpassword123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert response.data["non_field_errors"] == [
            "Не удалось войти с предоставленными учетными данными."
        ]

    def test_user_without_email_or_password(self, api_client):
        """Тест авторизации без указания почты."""
        url = reverse("login")
        data = {"email": "", "password": "123456"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["email"][0] == "This field may not be blank."

    def test_user_with_empty_fields(self, api_client):
        """Тест авторизации без указания почты и пароля."""
        url = reverse("login")
        data = {"email": None, "password": None}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["email"][0] == "This field may not be null."
        assert response.data["password"][0] == "This field may not be null."


    def test_force_validate_method(self):
        """Тест: Прямой вызов validate() с неполными данными."""
        serializer = LoginSerializer()
        
        data = {"email": "", "password": "pass"}
        validated_data = serializer.validate(data)
        
        assert validated_data["user"] is None
