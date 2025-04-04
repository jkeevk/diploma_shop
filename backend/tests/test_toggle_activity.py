import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import User


@pytest.mark.django_db
class TestToggleUserActivityView:
    """Набор тестов для управления активностью пользователей через API."""

    def test_admin_can_toggle_user_activity(self, api_client, admin, customer):
        """
        Тест: Администратор может изменить активность другого пользователя.
        Проверки:
        - Статус 200 OK
        - Корректное сообщение об успехе
        - Фактическое изменение статуса в БД
        """
        api_client.force_authenticate(user=admin)
        url = reverse("toggle-user-activity", kwargs={"user_id": customer.id})

        response = api_client.post(url)
        customer.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert "активность пользователя" in response.data["message"].lower()
        assert customer.is_active is False

    def test_admin_cannot_toggle_own_activity(self, api_client, admin):
        """
        Тест: Администратор не может изменить активность своего аккаунта.
        Ожидаемый результат:
        - Статус 403 Forbidden
        - Сообщение об ошибке доступа
        """
        api_client.force_authenticate(user=admin)
        url = reverse("toggle-user-activity", kwargs={"user_id": admin.id})

        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "своего аккаунта" in response.data["error"].lower()

    def test_regular_user_cannot_toggle_activity(self, api_client, customer):
        """
        Тест: Обычный пользователь не может изменять активность других.
        Ожидаемый результат:
        - Статус 403 Forbidden
        - Отсутствие изменений в БД
        """
        another_user = User.objects.create_user(
            email="another@example.com", password="testpass"
        )
        api_client.force_authenticate(user=customer)
        url = reverse("toggle-user-activity", kwargs={"user_id": another_user.id})

        response = api_client.post(url)
        another_user.refresh_from_db()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert another_user.is_active is True

    def test_toggle_nonexistent_user_returns_404(self, api_client, admin):
        """
        Тест: Попытка изменения активности несуществующего пользователя.
        Ожидаемый результат:
        - Статус 404 Not Found
        - Сообщение об ошибке
        """
        api_client.force_authenticate(user=admin)
        url = reverse("toggle-user-activity", kwargs={"user_id": 9999})

        response = api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no user matches the given query" in response.data["detail"].lower()
