import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from backend.models import User
from unittest.mock import patch

@pytest.fixture
def supplier():
    return User.objects.create_user(
        email="supplier@example.com",
        password="strongpassword123",
        first_name="Supplier",
        last_name="User",
        role="supplier",
        is_active=True
    )

@pytest.fixture
def admin():
    return User.objects.create_user(
        email="admin@example.com",
        password="strongpassword123",
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True
    )

@pytest.fixture
def customer():
    return User.objects.create_user(
        email="customer@example.com",
        password="strongpassword123",
        first_name="Customer",
        last_name="User",
        role="customer",
        is_active=True
    )

@pytest.mark.django_db
class TestPartnerImportView:
    """
    Тесты для представления PartnerImportView.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    @patch("backend.views.import_products_task.delay")
    def test_partner_import_success(self, mock_import_task, admin):
        """
        Тест успешного запуска задачи импорта.
        """
        self.client.force_authenticate(user=admin)

        mock_import_task.return_value = {"message": "Данные успешно импортированы"}

        url = reverse("partner-export")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"message": "Задача на импорт данных поставлена в очередь"}
        mock_import_task.assert_called_once()

    @patch("backend.views.import_products_task.delay")
    def test_partner_import_error(self, mock_import_task, admin):
        """
        Тест ошибки при запуске задачи импорта.
        """
        self.client.force_authenticate(user=admin)

        mock_import_task.side_effect = Exception("Ошибка при запуске задачи")

        url = reverse("partner-export")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {"error": "Ошибка при запуске задачи"}
        mock_import_task.assert_called_once()

    def test_partner_import_permission_denied(self, customer):
        """
        Тест проверки прав доступа для пользователя с ролью customer.
        """
        self.client.force_authenticate(user=customer)

        url = reverse("partner-export")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(response.data["detail"])
