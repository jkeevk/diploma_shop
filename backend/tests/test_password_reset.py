import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from backend.models import User
from backend.serializers import PasswordResetConfirmSerializer
from unittest.mock import patch
from django.core import mail
from celery import current_app


@pytest.mark.django_db
class TestPasswordResetView:
    """Тесты для представления сброса пароля."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Настройка тестового клиента API и конфигурации Celery."""
        self.client = api_client
        current_app.conf.task_always_eager = True

    @patch("backend.signals.TESTING", False)
    def test_password_reset_success(self, api_client, customer):
        """
        Проверка успешного запроса на сброс пароля.

        Ожидаемый результат: возвращается статус 200 и сообщение о том,
        что ссылка для сброса пароля отправлена на email.
        """
        url = reverse("password-reset")
        response = api_client.post(url, {"email": customer.email})

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["detail"] == "Ссылка для сброса пароля отправлена на email."
        )

        assert len(mail.outbox) == 1, "Письмо не было отправлено!"
        email = mail.outbox[0]

        assert email.subject == "Password Reset"
        assert customer.email in email.to
        assert "reset" in email.body.lower()

    def test_password_reset_user_not_found(self, api_client):
        """
        Проверка обработки несуществующего пользователя.

        Ожидаемый результат: возвращается статус 400 и сообщение о том,
        что пользователь с таким email не найден.
        """
        url = reverse("password-reset")
        response = api_client.post(url, {"email": "nonexistent@example.com"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert (
            response.data["email"]["email"][0]
            == "Пользователь с таким email не найден."
        )

    def test_password_reset_invalid_email(self, api_client):
        """
        Проверка валидации неверного формата email.

        Ожидаемый результат: возвращается статус 400 и сообщение о неверном формате email.
        """
        url = reverse("password-reset")
        response = api_client.post(url, {"email": "invalid_email"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert response.data["email"][0] == "Enter a valid email address."


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Тесты для эндпоинта подтверждения сброса пароля."""

    def create_test_user(self):
        """Создание тестового пользователя."""
        return User.objects.create_user(
            email="testuser@example.com", password="oldpassword123"
        )

    def test_success(self, api_client):
        """
        Проверка успешной смены пароля.

        Ожидаемый результат: возвращается статус 200 и новый пароль успешно сохраняется.
        """

        user = self.create_test_user()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = reverse("password-reset-confirm", kwargs={"uidb64": uid, "token": token})
        response = api_client.post(url, {"new_password": "NewSecurePassword123!"})

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("NewSecurePassword123!")

    def test_invalid_token(self, api_client):
        """
        Проверка обработки недействительного токена.

        Ожидаемый результат: возвращается статус 400 и сообщение о недействительном токене.
        """

        user = self.create_test_user()
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse(
            "password-reset-confirm", kwargs={"uidb64": uid, "token": "invalid_token"}
        )
        response = api_client.post(url, {"new_password": "NewPassword123"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.data
        assert response.data["token"][0] == "Недействительный токен сброса пароля"

    def test_invalid_uid(self, api_client):
        """
        Проверка обработки неверного идентификатора пользователя.

        Ожидаемый результат: возвращается статус 400 и сообщение об ошибке в uid.
        """

        url = reverse(
            "password-reset-confirm",
            kwargs={"uidb64": "invalid_uid", "token": "any_token"},
        )

        response = api_client.post(url, {"new_password": "NewPassword123"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data

    def test_weak_password(self, api_client):
        """
        Проверка валидации слабого пароля.

        Ожидаемый результат: возвращается статус 400 и сообщение о том,
        что пароль слишком короткий или слабый.
        """

        user = self.create_test_user()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = reverse("password-reset-confirm", kwargs={"uidb64": uid, "token": token})
        response = api_client.post(url, {"new_password": "123"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert "too short" in response.data["non_field_errors"][0].lower()


@pytest.mark.django_db
class TestPasswordResetConfirmSerializer:
    """Тесты для сериализатора подтверждения сброса пароля."""

    @pytest.fixture
    def valid_context(self):
        """Фикстура с валидным контекстом для сериализатора."""
        user = User.objects.create_user(email="test@example.com", password="oldpass")
        return {
            "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        }

    def test_valid_data(self, valid_context):
        """Проверка валидации корректных данных."""
        serializer = PasswordResetConfirmSerializer(
            data={"new_password": "ValidPassword123!"}, context=valid_context
        )
        assert serializer.is_valid()

    def test_invalid_password(self, valid_context):
        """Проверка обработки некорректного пароля."""
        serializer = PasswordResetConfirmSerializer(
            data={"new_password": "short"}, context=valid_context
        )
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
