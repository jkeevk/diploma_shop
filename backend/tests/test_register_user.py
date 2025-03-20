import re
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from celery import current_app
from backend.models import User


@pytest.mark.django_db
class TestUserRegistration:
    def setup_method(self):
        """
        Настройка перед каждым тестом.
        """
        current_app.conf.task_always_eager = True

        self.data = {
            "email": "test2@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
        }

    def test_register_user(self, api_client):
        """
        Тест успешной регистрации пользователя.
        """
        url = reverse("user-register")
        response = api_client.post(url, self.data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.get(email=self.data["email"])
        assert user.confirmation_token is not None
        assert not user.is_active

    def test_email_sent_after_registration(self, api_client):
        """
        Тест отправки письма с токеном после регистрации.
        """
        url = reverse("user-register")
        api_client.post(url, self.data, format="json")

        assert len(mail.outbox) == 1

        email = mail.outbox[0]
        assert email.subject == "Confirm Your Registration"
        assert "Please click the link below to confirm your registration" in email.body

        token_match = re.search(
            r"http[s]?://[^/]+/user/register/confirm/([a-f0-9]+)", email.body
        )
        assert token_match is not None, "Токен не найден в письме"

        self.token = token_match.group(1)

    def test_confirm_registration_with_valid_token(self, api_client):
        """
        Тест подтверждения регистрации с валидным токеном.
        """
        self.test_email_sent_after_registration(api_client)

        url_confirm = reverse("user-register-confirm", kwargs={"token": self.token})
        response = api_client.get(url_confirm)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "Status": "success",
            "Message": "Ваш аккаунт успешно активирован.",
        }

        user = User.objects.get(email=self.data["email"])
        assert user.is_active
        assert user.confirmation_token is None

    def test_confirm_registration_with_invalid_token(self, api_client):
        """
        Тест подтверждения регистрации с невалидным токеном.
        """
        invalid_token = "invalid_token_123"
        url_confirm = reverse("user-register-confirm", kwargs={"token": invalid_token})
        response = api_client.get(url_confirm)

        assert response.status_code == status.HTTP_404_NOT_FOUND
