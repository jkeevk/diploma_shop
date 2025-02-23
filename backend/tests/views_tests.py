from backend.tasks import run_pytest
from celery.result import AsyncResult
from backend.permissions import check_role_permission
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from backend.swagger_configs import SWAGGER_CONFIGS


@SWAGGER_CONFIGS["run_pytest_schema"]
class RunPytestView(APIView):
    """
    Представление для запуска pytest.
    Доступна только для администраторов.
    """

    permission_classes = [check_role_permission("admin")]

    def post(self, request, *args, **kwargs):
        """
        Запускает pytest и возвращает результат.
        """
        task = run_pytest.delay()

        return Response(
            {"task_id": task.id},
            status=status.HTTP_202_ACCEPTED,
        )

@SWAGGER_CONFIGS["check_pytest_task_schema"]
class CheckPytestTaskView(APIView):
    """
    Представление для проверки статуса задачи pytest.
    Возвращает удобный для человека результат.
    """

    def parse_pytest_output(self, output):
        """
        Парсит вывод pytest и извлекает количество пройденных, проваленных тестов и ошибок,
        а также списки проваленных и успешных тестов.
        """
        summary_pattern = r"(\d+) passed.*?(\d+) failed.*?(\d+) errors|(\d+) passed.*?(\d+) failed|(\d+) passed"
        passed_tests_pattern = r"PASSED"
        failed_tests_pattern = r"FAILED|ERROR"

        summary_match = re.search(summary_pattern, output)
        if summary_match:
            passed = int(
                summary_match.group(1)
                or summary_match.group(4)
                or summary_match.group(6)
                or 0
            )
            failed = int(summary_match.group(2) or summary_match.group(5) or 0)
            errors = int(summary_match.group(3) or 0)
        else:
            passed = failed = errors = 0

        successful_tests = []
        for line in output.splitlines():
            if re.search(passed_tests_pattern, line):
                test_name = line.split("::")[-1].split(" ")[0]
                successful_tests.append(test_name)

        failed_tests = []
        in_failures_section = False
        for line in output.splitlines():
            if "FAILURES" in line:
                in_failures_section = True
                continue

            if in_failures_section:
                if "::" in line and ("FAILED" in line or "ERROR" in line):
                    test_name = line.split("::")[-1].split(" ")[0]
                    failed_tests.append(test_name)

        if failed == 0 and len(failed_tests) > 0:
            failed = len(failed_tests)

        return {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
        }

    def get(self, request, task_id, *args, **kwargs):
        """
        Возвращает статус и результат задачи.
        """
        task = AsyncResult(task_id)
        if task.ready():
            if task.successful():
                result = task.result
                if "error" in result:
                    return Response(
                        {
                            "status": "ERROR",
                            "message": result["error"],
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                pytest_output = result.get("output", "")
                parsed_result = self.parse_pytest_output(pytest_output)

                response_data = {
                    "status": "SUCCESS",
                    "summary": {
                        "passed": parsed_result["passed"],
                        "failed": parsed_result["failed"],
                        "errors": parsed_result["errors"],
                    },
                    "successful_tests": parsed_result["successful_tests"],
                    "failed_tests": parsed_result["failed_tests"],
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "status": "FAILURE",
                        "message": "Задача завершилась с ошибкой.",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"status": "PENDING", "message": "Задача ещё выполняется."},
                status=status.HTTP_202_ACCEPTED,
            )
