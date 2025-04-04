from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

AUTH_ERROR_RESPONSES = {
    401: {
        "description": "Пользователь не авторизован",
        "content": {"application/json": {}},
    },
    403: {
        "description": "Доступ запрещен",
        "content": {"application/json": {}},
    },
}

AUTH_ERROR_EXAMPLES = [
    OpenApiExample(
        name="Ошибка: пользователь не авторизован",
        value={"detail": "Пожалуйста, войдите в систему."},
        status_codes=["401"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: доступ запрещен",
        value={"detail": "У вас недостаточно прав для выполнения этого действия."},
        status_codes=["403"],
        response_only=True,
    ),
]

TEST_SCHEMAS = {
    "run_pytest_schema": extend_schema(
        summary="Запуск pytest",
        description="Эндпоинт для запуска pytest. Доступен только для администраторов.",
        responses={
            202: {
                "description": "Задача на выполнение pytest успешно создана.",
                "content": {"application/json": {}},
            },
            **AUTH_ERROR_RESPONSES,
        },
        examples=[
            OpenApiExample(
                name="Задача на выполнение pytest успешно создана",
                value={"task_id": "550e8400-e29b-41d4-a716-446655440000"},
                status_codes=["202"],
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
    "check_pytest_task_schema": extend_schema(
        summary="Проверка статуса задачи pytest",
        description="Эндпоинт для проверки статуса задачи pytest. Возвращает результат выполнения тестов.",
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="ID задачи, возвращенный при запуске pytest.",
            ),
        ],
        responses={
            200: {
                "description": "Результат выполнения тестов.",
                "content": {"application/json": {}},
            },
            202: {
                "description": "Задача ещё выполняется.",
                "content": {"application/json": {}},
            },
            500: {
                "description": "Ошибка при выполнении задачи.",
                "content": {"application/json": {}},
            },
            **AUTH_ERROR_RESPONSES,
        },
        examples=[
            OpenApiExample(
                name="Результат выполнения тестов",
                value={
                    "status": "SUCCESS",
                    "summary": {
                        "passed": 5,
                        "failed": 1,
                        "errors": 0,
                    },
                    "successful_tests": ["test_example_1", "test_example_2"],
                    "failed_tests": ["test_example_3"],
                },
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Задача ещё выполняется",
                value={"status": "PENDING", "message": "Задача ещё выполняется."},
                status_codes=["202"],
            ),
            OpenApiExample(
                name="Ошибка при выполнении задачи",
                value={"status": "FAILURE", "message": "Задача завершилась с ошибкой."},
                status_codes=["500"],
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
    "test_force_sentry_error_schema": extend_schema(
        summary="Запуск принудительной ошибки для Sentry",
        description="Эндпоинт для принудительного запуска ошибки для отправки в Sentry. Доступен только для администраторов.",
        responses={
            500: {
                "description": "Тестовая ошибка успешно сгенерирована и отправлена в Sentry",
                "content": {"application/json": {}},
            },
            **AUTH_ERROR_RESPONSES,
        },
        examples=[
            OpenApiExample(
                name="Тестовая ошибка Sentry",
                value={"error": "Internal server error"},
                status_codes=["500"],
                description="Пример ответа при успешной генерации тестовой ошибки",
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
}
