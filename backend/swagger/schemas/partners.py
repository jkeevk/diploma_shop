from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
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

FILE_UPLOAD_SCHEMA = {
    "multipart/form-data": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "format": "binary",
            }
        },
    }
}

PARTNER_SCHEMAS = {
    "partner_update_schema": extend_schema(
        summary="Обновление каталога поставщика",
        description=(
            "Эндпоинт для обновления каталога поставщика. Требует multipart/form-data в теле запроса. "
            "Файл должен быть в формате JSON. Используется для загрузки данных о товарах."
        ),
        tags=["Поставщики"],
        request=FILE_UPLOAD_SCHEMA,
        responses={
            200: {
                "description": "Данные успешно загружены",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Неверный запрос (неверный файл или файл не загружен)",
                "content": {"application/json": {}},
            },
            **AUTH_ERROR_RESPONSES,
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                value={"message": "Задача на загрузку данных поставлена в очередь"},
                status_codes=["200"],
                response_only=True,
            ),
            OpenApiExample(
                name="Неверный запрос",
                value={
                    "file": [
                        "The submitted data was not a file. Check the encoding type on the form."
                    ]
                },
                status_codes=["400"],
                response_only=True,
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
    "partner_import_schema": extend_schema(
        summary="Импорт данных поставщика",
        description="Эндпоинт для импорта данных поставщика. Возвращает ID задачи.",
        tags=["Поставщики"],
        responses={
            202: {
                "description": "Задача на импорт данных поставлена в очередь",
                "content": {"application/json": {}},
            },
            **AUTH_ERROR_RESPONSES,
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                value={"task_id": "9e826fcd-4eaf-470b-b0d8-2d55ef809177"},
                status_codes=["202"],
                response_only=True,
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
    "check_partner_import_schema": extend_schema(
        summary="Проверка статуса задачи на импорт данных поставщика",
        tags=["Поставщики"],
        description=(
            "Эндпоинт для проверки статуса задачи импорта. "
            "Возвращает текущий статус и результат выполнения."
        ),
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID задачи импорта (обязательный параметр)",
                required=True,
            )
        ],
        responses={
            200: {
                "description": "Статус задачи",
                "content": {"application/json": {}},
            },
            **AUTH_ERROR_RESPONSES,
        },
        examples=[
            OpenApiExample(
                name="Успешное выполнение",
                value={"status": "SUCCESS", "data": ["Imported data"]},
                status_codes=["200"],
                response_only=True,
            ),
            OpenApiExample(
                name="Задача в процессе",
                value={"status": "PENDING"},
                status_codes=["200"],
                response_only=True,
            ),
            OpenApiExample(
                name="Ошибка выполнения",
                value={"status": "FAILURE", "error": "Ошибка валидации данных"},
                status_codes=["200"],
                response_only=True,
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
    "partner_orders_schema": extend_schema(
        summary="Получить подтвержденные заказы для поставщика",
        tags=["Поставщики"],
        description=(
            "Возвращает список подтвержденных заказов для магазина, "
            "связанного с текущим пользователем."
        ),
        responses={
            200: {
                "description": "Список подтвержденных заказов",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Ошибка, если пользователь не связан с магазином.",
                "content": {"application/json": {}},
            },
            **AUTH_ERROR_RESPONSES,
        },
        examples=[
            OpenApiExample(
                name="Список подтвержденных заказов",
                value=[{"id": 1, "status": "confirmed", "items": []}],
                status_codes=["200"],
                response_only=True,
            ),
            OpenApiExample(
                name="Ошибка, если пользователь не связан с магазином",
                value={"detail": "Вы не связаны с магазином."},
                status_codes=["400"],
                response_only=True,
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
}
