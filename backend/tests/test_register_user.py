import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from celery import current_app
from backend.models import User
from django.conf import settings
from django.test import override_settings


@pytest.mark.django_db
class TestUserRegistration:
    """Набор тестов для процесса регистрации пользователей."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Настройка тестового клиента и базовых данных для регистрации."""
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
        """Тест: Успешная регистрация с корректными данными.

        Ожидаемый результат:
        - Статус ответа 201 (Created).
        - Статус в ответе 'success'.
        - Пользователь создан, но не активен.
        """
        url = reverse("register")
        response = self.client.post(url, self.base_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"

        user = User.objects.get(email=self.base_data["email"])
        assert not user.is_active

    def test_registration_with_invalid_role(self):
        """Тест: Обработка невалидной роли при регистрации.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке 'Неверная роль'.
        """
        data = {**self.base_data, "role": "invalid_role"}
        url = reverse("register")

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверная роль" in str(response.data["errors"]["role"][0])

    def test_registration_with_existing_email(self):
        """Тест: Регистрация с уже существующим email.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке 'уже существует' для email.
        """
        User.objects.create_user(**self.base_data)
        url = reverse("register")

        response = self.client.post(url, self.base_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже существует" in str(response.data["errors"]["email"][0]).lower()

    def test_registration_with_missing_fields(self):
        """Тест: Валидация отсутствия обязательных полей при регистрации.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщения об ошибках для полей 'email', 'password' и 'role'.
        """
        url = reverse("register")
        response = self.client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data["errors"]

        assert all(field in errors for field in ["email", "password", "role"])
        assert "обязателен для заполнения" in str(errors["email"][0])
        assert "обязателен для заполнения" in str(errors["password"][0])
        assert "Роль обязательна для заполнения" in str(errors["role"][0])

    def test_password_validation(self):
        """Тест: Валидация слабого пароля при регистрации.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке о том, что пароль слишком короткий.
        """
        data = {**self.base_data, "password": "123"}
        url = reverse("register")

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "too short" in str(response.data["errors"]["password"][0]).lower()

    def test_email_sending_after_registration(self):
        """Тест: Отправка письма с подтверждением после регистрации.

        Ожидаемый результат:
        - Письмо отправлено (должно быть одно в outbox).
        - Тема письма 'Confirm Your Registration'.
        - Email получателя соответствует зарегистрированному пользователю.
        """
        with override_settings(
            TESTING=False, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            url = reverse("register")
            self.client.post(url, self.base_data)

            assert len(mail.outbox) == 1
            email = mail.outbox[0]

            assert email.subject == "Confirm Your Registration"
            assert self.base_data["email"] in email.to
            assert "confirm" in email.body.lower()

    def test_successful_email_confirmation(self):
        """Тест: Успешное подтверждение email после регистрации.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Пользователь активирован после подтверждения.
        """
        with override_settings(
            TESTING=False, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            self.client.post(reverse("register"), self.base_data)
            user = User.objects.get(email=self.base_data["email"])

            url = reverse("register-confirm", kwargs={"token": user.confirmation_token})
            response = self.client.get(url)

            assert response.status_code == status.HTTP_200_OK
            user.refresh_from_db()
            assert user.is_active

    def test_invalid_confirmation_token(self):
        """Тест: Обработка невалидного токена подтверждения.

        Ожидаемый результат:
        - Статус ответа 404 (Not Found).
        """
        url = reverse("register-confirm", kwargs={"token": "invalid_token"})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
