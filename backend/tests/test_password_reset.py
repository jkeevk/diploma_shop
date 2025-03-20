import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from unittest.mock import patch
from backend.models import User
from backend.serializers import PasswordResetConfirmSerializer


@pytest.mark.django_db
class TestPasswordResetView:
    def test_password_reset_success(self, api_client, customer):
        """Тест успешного запроса на сброс пароля."""

        url = reverse("password-reset")
        response = api_client.post(url, {"email": customer.email})

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["detail"] == "Ссылка для сброса пароля отправлена на email."
        )

    def test_password_reset_user_not_found(self, api_client):
        """Тест запроса на сброс пароля для несуществующего пользователя."""
        url = reverse("password-reset")
        response = api_client.post(url, {"email": "nonexistent@example.com"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert (
            response.data["email"]["email"][0]
            == "Пользователь с таким email не найден."
        )

    def test_password_reset_invalid_email(self, api_client):
        """Тест запроса на сброс пароля с недействительным email."""
        url = reverse("password-reset")
        response = api_client.post(url, {"email": "invalid_email"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert response.data["email"][0] == "Enter a valid email address."


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    def test_password_reset_confirm_success(self, api_client):
        """
        Тест успешного подтверждения сброса пароля.
        """
        user = User.objects.create_user(
            email="testuser@example.com", password="oldpassword123"
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        with patch(
            "django.contrib.auth.tokens.default_token_generator.check_token",
            return_value=True,
        ):
            url = reverse(
                "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
            )
            response = api_client.post(url, {"new_password": "newpassword123"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "Пароль успешно изменён."}

        user.refresh_from_db()
        assert user.check_password("newpassword123")

    def test_password_reset_confirm_invalid_token(self, api_client):
        """
        Тест подтверждения сброса пароля с недействительным токеном.
        """
        user = User.objects.create_user(
            email="testuser@example.com", password="oldpassword123"
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = "invalid-token"

        with patch(
            "django.contrib.auth.tokens.default_token_generator.check_token",
            return_value=False,
        ):
            url = reverse(
                "password_reset_confirm", kwargs={"uidb64": uid, "token": invalid_token}
            )
            response = api_client.post(url, {"new_password": "newpassword123"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"detail": "Недействительный токен."}

    def test_password_reset_confirm_user_not_found(self, api_client):
        """
        Тест подтверждения сброса пароля для несуществующего пользователя.
        """
        uid = urlsafe_base64_encode(force_bytes(999))
        token = "valid-token"

        url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        response = api_client.post(url, {"new_password": "newpassword123"})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"detail": "Пользователь не найден."}

    def test_password_reset_confirm_invalid_password(self, api_client):
        """
        Тест подтверждения сброса пароля с некорректным новым паролем.
        """
        user = User.objects.create_user(
            email="testuser@example.com", password="oldpassword123"
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        with patch(
            "django.contrib.auth.tokens.default_token_generator.check_token",
            return_value=True,
        ):
            url = reverse(
                "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
            )
            response = api_client.post(url, {"new_password": "short"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
        assert "This password is too short." in response.data["new_password"][0]


class TestPasswordResetConfirmSerializer:
    def test_password_reset_confirm_serializer_valid(self):
        """
        Тест валидации корректного нового пароля.
        """
        serializer = PasswordResetConfirmSerializer(
            data={"new_password": "validpassword123"}
        )
        assert serializer.is_valid()

    def test_password_reset_confirm_serializer_invalid(self):
        """
        Тест валидации некорректного нового пароля.
        """
        serializer = PasswordResetConfirmSerializer(data={"new_password": "short"})
        assert not serializer.is_valid()
        assert "new_password" in serializer.errors
        assert "This password is too short." in serializer.errors["new_password"][0]
