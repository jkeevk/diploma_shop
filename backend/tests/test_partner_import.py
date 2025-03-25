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

    @patch("backend.views.AsyncResult")
    def test_partner_import_status_success(self, mock_async_result, api_client, admin):
        """
        Тест успешного получения статуса задачи импорта.
        """
        api_client.force_authenticate(user=admin)

        mock_task_id = str(uuid.uuid4())
        mock_result = {
            "status": "success",
            "data": {"some_key": "some_value"}
        }
        mock_async_result.return_value = MagicMock(
            status="SUCCESS",
            ready=lambda: True,
            successful=lambda: True,
            result=mock_result
        )

        url = reverse("import-status", args=[mock_task_id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "SUCCESS"
        assert response.data["data"] == {"some_key": "some_value"}
        assert "error" not in response.data

    @patch("backend.views.AsyncResult")
    def test_partner_import_status_failure(self, mock_async_result, api_client, admin):
        """
        Тест получения статуса задачи импорта с ошибкой.
        """
        api_client.force_authenticate(user=admin)

        mock_task_id = str(uuid.uuid4())
        mock_result = {
            "status": "error",
            "message": "Some error occurred"
        }
        mock_async_result.return_value = MagicMock(
            status="FAILURE",
            ready=lambda: True,
            successful=lambda: False,
            result=mock_result
        )

        url = reverse("import-status", args=[mock_task_id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "FAILURE"
        assert response.data["error"] == "Task failed"

    @patch("backend.views.AsyncResult")
    def test_task_not_ready(self, mock_async_result, api_client, admin):
        """
        Тест, который проверяет выполнение блока кода, когда задача не готова.
        """
        api_client.force_authenticate(user=admin)

        mock_task_id = str(uuid.uuid4())
        mock_result = {
            "status": "PENDING",
            "data": {"some_key": "some_value"}
        }

        mock_async_result.return_value = MagicMock(
            status="PENDING",
            ready=lambda: False,
            successful=lambda: False,
            result=mock_result
        )
        url = reverse("import-status", args=[mock_task_id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "PENDING"
        assert "data" not in response.data
