import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestRunPytestAPI:
    """Тесты API для запуска и проверки задач pytest."""

    def test_admin_user_can_trigger_pytest_run(
        self, api_client: APIClient, admin: User
    ) -> None:
        """Тест: Запуск тестов администратором.

        Ожидаемый результат:
        - Статус ответа 202 (Accepted).
        - Ответ содержит идентификатор задачи.
        """
        api_client.force_authenticate(user=admin)
        url = reverse("run-pytest")
        with patch("backend.tasks.run_pytest.delay") as mock_task:
            mock_task.return_value.id = "test-task-id"
            response = api_client.get(url)

            assert response.status_code == status.HTTP_202_ACCEPTED
            assert response.data == {"task_id": "test-task-id"}

    def test_non_admin_user_forbidden_to_run_pytest(
        self, api_client: APIClient, customer: User
    ) -> None:
        """Тест: Попытка запуска тестов обычным пользователем.

        Ожидаемый результат:
        - Статус ответа 403 (Forbidden).
        """
        api_client.force_authenticate(user=customer)
        response = api_client.get(reverse("run-pytest"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pytest_task_returns_correct_task_id(
        self, api_client: APIClient, admin: User
    ) -> None:
        """Тест: Корректное создание задачи запуска тестов.

        Ожидаемый результат:
        - Статус ответа 202 (Accepted).
        - Идентификатор задачи соответствует ожидаемому.
        - Задача вызывается с параметром enable_coverage=True.
        """
        api_client.force_authenticate(user=admin)
        with patch("backend.tasks.run_pytest.delay") as mock_task:
            mock_task.return_value.id = "test-123"
            response = api_client.get(reverse("run-pytest"))

            assert response.data["task_id"] == "test-123"
            mock_task.assert_called_once_with(enable_coverage=True)

    def test_unauthenticated_user_access_denied_for_task_check(
        self, api_client: APIClient
    ) -> None:
        """Тест: Проверка статуса задачи без аутентификации.

        Ожидаемый результат:
        - Статус ответа 401 (Unauthorized).
        - Сообщение о необходимости авторизации.
        """
        url = reverse("check-pytest", kwargs={"task_id": "dummy-task"})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Пожалуйста, войдите в систему."

    def test_check_task_returns_pending_status(
        self, api_client: APIClient, admin: User
    ) -> None:
        """Тест: Проверка статуса выполняющейся задачи.

        Ожидаемый результат:
        - Статус ответа 202 (Accepted).
        - Сообщение о выполнении задачи.
        """
        api_client.force_authenticate(user=admin)
        task_id = "pending-task-123"

        with patch("celery.result.AsyncResult") as mock_result:
            mock_result.return_value.ready.return_value = False
            mock_result.return_value.failed.return_value = False

            url = reverse("check-pytest", kwargs={"task_id": task_id})
            response = api_client.get(url)

            assert response.status_code == status.HTTP_202_ACCEPTED
            assert response.data == {
                "status": "PENDING",
                "message": "Задача ещё выполняется.",
            }
