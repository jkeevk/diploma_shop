import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestRunPytestView:
    """
    Тесты для представления запуска тестов с использованием Celery.
    """

    def test_admin_access(self, api_client: APIClient, admin: User) -> None:
        """
        Проверяем, что только администратор может запускать тесты.
        """
        api_client.force_authenticate(user=admin)
        url = reverse("run-pytest")
        with patch("backend.tasks.run_pytest.delay") as mock_run_pytest:
            mock_run_pytest.return_value.id = "test-task-id"
            response = api_client.get(url)
            assert response.status_code == status.HTTP_202_ACCEPTED
            assert "task_id" in response.data

    def test_non_admin_access(self, api_client: APIClient, customer: User) -> None:
        """
        Проверяем, что обычный пользователь не может запускать тесты.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("run-pytest")
        with patch("backend.tasks.run_pytest.delay") as mock_run_pytest:
            mock_run_pytest.return_value.id = "test-task-id"
            response = api_client.get(url)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_run_pytest_task_creation(self, api_client: APIClient, admin: User) -> None:
        """
        Проверяем, что задача run_pytest создается и возвращается task_id.
        """
        api_client.force_authenticate(user=admin)
        url = reverse("run-pytest")

        with patch("backend.tasks.run_pytest.delay") as mock_run_pytest:
            mock_run_pytest.return_value.id = "test-task-id"
            response = api_client.get(url)

            assert response.status_code == status.HTTP_202_ACCEPTED
            assert response.data == {"task_id": "test-task-id"}
            mock_run_pytest.assert_called_once_with(enable_coverage=True)

    def test_check_pytest_task_view_authorization(self, api_client: APIClient) -> None:
        """
        Проверяем, что неавторизованный пользователь не может получить доступ
        к представлению проверки задачи.
        """
        response = api_client.get("/tests/check-pytest-task/some-task-id/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "Вы не авторизованы. Пожалуйста, войдите в систему."
        }

    def test_check_pytest_task_view_pending(
        self, api_client: APIClient, admin: User
    ) -> None:
        """
        Проверяем ответ для задачи, которая ещё выполняется.
        """
        api_client.force_authenticate(user=admin)

        task_id = "pending-task-id"

        with patch("celery.result.AsyncResult") as mock_async_result:
            mock_task = mock_async_result.return_value
            mock_task.ready.return_value = False
            mock_task.failed.return_value = False

            response = api_client.get(f"/tests/check-pytest-task/{task_id}/")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data == {
            "status": "PENDING",
            "message": "Задача ещё выполняется.",
        }
