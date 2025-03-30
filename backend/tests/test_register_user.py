import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from celery import current_app
from backend.models import User
from unittest.mock import patch


@pytest.mark.django_db
class TestUserRegistration:
    """Тесты для процесса регистрации пользователей."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.client = api_client
        self.base_data = {
            "email": "test2@example.com",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
        }
        current_app.conf.task_always_eager = True

    def test_successful_registration(self):
        """Проверка успешной регистрации с корректными данными."""
        url = reverse("user-register")
        response = self.client.post(url, self.base_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"

        user = User.objects.get(email=self.base_data["email"])
        assert not user.is_active

    def test_registration_with_invalid_role(self):
        """Проверка обработки невалидной роли."""
        data = {**self.base_data, "role": "invalid_role"}
        url = reverse("user-register")

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверная роль" in str(response.data["errors"]["role"][0])

    def test_registration_with_existing_email(self):
        """Проверка регистрации с уже существующим email."""
        User.objects.create_user(**self.base_data)
        url = reverse("user-register")

        response = self.client.post(url, self.base_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже существует" in str(response.data["errors"]["email"][0]).lower()

    def test_registration_with_missing_fields(self):
        """Проверка валидации отсутствия обязательных полей."""
        url = reverse("user-register")
        response = self.client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data["errors"]
        assert all(field in errors for field in ["email", "password", "role"])
        assert "обязателен для заполнения" in str(errors["email"][0])
        assert "обязателен для заполнения" in str(errors["password"][0])
        assert "Роль обязательна для заполнения" in str(errors["role"][0])

    def test_password_validation(self):
        """Проверка валидации слабого пароля."""
        data = {**self.base_data, "password": "123"}
        url = reverse("user-register")

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "too short" in str(response.data["errors"]["password"][0]).lower()

    @patch("backend.signals.TESTING", False)
    def test_email_sending_after_registration(self):
        """Проверка отправки письма с подтверждением."""
        url = reverse("user-register")
        self.client.post(url, self.base_data)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        assert email.subject == "Confirm Your Registration"
        assert self.base_data["email"] in email.to
        assert "confirm" in email.body.lower()

    @patch("backend.signals.TESTING", False)
    def test_successful_email_confirmation(self):
        """Проверка успешного подтверждения email."""
        self.client.post(reverse("user-register"), self.base_data)
        user = User.objects.get(email=self.base_data["email"])

        url = reverse(
            "user-register-confirm", kwargs={"token": user.confirmation_token}
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active

    def test_invalid_confirmation_token(self):
        """Проверка обработки невалидного токена подтверждения."""
        url = reverse("user-register-confirm", kwargs={"token": "invalid_token"})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
