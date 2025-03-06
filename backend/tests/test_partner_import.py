import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch, MagicMock
import uuid


@pytest.mark.django_db
class TestPartnerImportView:
    """
    Тесты для представления PartnerImportView.
    """

    @patch("backend.views.import_products_task.delay")
    def test_partner_import_success(self, mock_import_task, api_client, admin):
        """
        Тест успешного запуска задачи импорта.
        """
        api_client.force_authenticate(user=admin)

        mock_task = MagicMock()
        mock_task.id = str(uuid.uuid4())

        mock_import_task.return_value = mock_task

        url = reverse("partner-import")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert isinstance(response.data["task_id"], str)
        assert len(response.data["task_id"]) > 0
        mock_import_task.assert_called_once()

    @patch("backend.views.import_products_task.delay")
    def test_partner_import_error(self, mock_import_task, api_client, admin):
        """
        Тест ошибки при запуске задачи импорта.
        """
        api_client.force_authenticate(user=admin)

        mock_import_task.side_effect = Exception("Ошибка при запуске задачи")

        url = reverse("partner-import")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {"error": "Ошибка при запуске задачи"}
        mock_import_task.assert_called_once()

    def test_partner_import_permission_denied(self, api_client, customer):
        """
        Тест проверки прав доступа для пользователя с ролью customer.
        """
        api_client.force_authenticate(user=customer)

        url = reverse("partner-import")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(response.data["detail"])
