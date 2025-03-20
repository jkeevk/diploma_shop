import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from backend.models import User


@pytest.mark.django_db
class TestToggleUserActivityView:
    def test_toggle_activity_success(self, api_client, admin, customer):
        """
        Тест успешного переключения активности пользователя администратором.
        """
        api_client.force_authenticate(user=admin)
        url = reverse("toggle-user-activity", kwargs={"user_id": customer.id})

        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["message"]
            == f"Активность пользователя {customer.email} (ID={customer.id}) изменена на {not customer.is_active}"
        )
        customer.refresh_from_db()
        assert customer.is_active == False

    def test_toggle_activity_self(self, api_client, admin):
        """
        Тест попытки изменения активности своего аккаунта.
        """
        api_client.force_authenticate(user=admin)
        url = reverse("toggle-user-activity", kwargs={"user_id": admin.id})

        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["error"]
            == "Вы не можете изменить активность своего аккаунта."
        )

    def test_toggle_activity_without_permission(self, api_client, customer):
        """
        Тест попытки изменения активности пользователя без прав администратора.
        """
        api_client.force_authenticate(user=customer)
        another_user = User.objects.create_user(
            email="another_user@example.com", password="anotherpassword"
        )
        url = reverse("toggle-user-activity", kwargs={"user_id": another_user.id})

        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_toggle_activity_user_not_found(self, api_client, admin):
        """
        Тест попытки переключения активности несуществующего пользователя.
        """
        api_client.force_authenticate(user=admin)
        url = reverse("toggle-user-activity", kwargs={"user_id": 999})

        response = api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
