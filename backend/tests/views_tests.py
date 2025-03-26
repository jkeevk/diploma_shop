# Celery
from celery.result import AsyncResult

# Local imports
from backend.permissions import check_role_permission
from backend.swagger_configs import SWAGGER_CONFIGS
from backend.tasks import run_pytest

# Rest Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class BaseTaskView(APIView):
    task_model = None

    def get_task_response(self, task_id):
        task = AsyncResult(task_id)
        if not task.ready():
            return Response(
                {"status": "PENDING", "message": "Задача ещё выполняется."},
                status.HTTP_202_ACCEPTED,
            )

        if task.failed():
            return Response(
                {"status": "ERROR", "message": str(task.result)},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return self.handle_success(task.result)

    def handle_success(self, result):
        raise NotImplementedError


@SWAGGER_CONFIGS["run_pytest_schema"]
class RunPytestView(APIView):
    permission_classes = [check_role_permission("admin")]

    def get(self, request):
        task = run_pytest.delay(enable_coverage=True)
        return Response({"task_id": task.id}, status.HTTP_202_ACCEPTED)


@SWAGGER_CONFIGS["check_pytest_task_schema"]
class CheckPytestTaskView(BaseTaskView):
    permission_classes = [check_role_permission("admin")]

    def handle_success(self, result):
        response_data = {
            "status": (
                "SUCCESS" if result["failed"] + result["errors"] == 0 else "HAS_ISSUES"
            ),
            "summary": {
                "passed": result["passed"],
                "failed": result["failed"],
                "errors": result["errors"],
            },
            "coverage": result.get("coverage"),
        }
        return Response(response_data, status.HTTP_200_OK)

    def get(self, request, task_id):
        return self.get_task_response(task_id)


@SWAGGER_CONFIGS["test_force_sentry_error_schema"]
class ForceSentryErrorAPIView(APIView):
    """
    API View для тестирования интеграции с Sentry.
    """

    permission_classes = [check_role_permission("admin")]

    def get(self, request):
        """
        Вызывает исключение для проверки работы Sentry.
        """
        raise ValueError("Это тестовая ошибка для Sentry!")
