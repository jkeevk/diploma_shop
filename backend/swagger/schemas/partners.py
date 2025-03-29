from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)


PARTNER_SCHEMAS = {
    "partner_update_schema": extend_schema(
        summary="Обновление каталога поставщика",
        description="Эндпоинт для обновления каталога поставщика. Требует multipart/form-data в теле запроса. Файл должен быть в формате JSON. Используется для загрузки данных о товарах.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                    }
                },
            }
        },
        responses={
            200: {
                "description": "Данные успешно загружены",
                "content": {
                    "application/json": {
                        "example": {"message": "Data uploaded successfully."}
                    }
                },
            },
            400: {
                "description": "Неверный запрос (неверный файл или файл не загружен)",
                "content": {
                    "application/json": {
                        "example": {"detail": "Invalid file or file not uploaded."}
                    }
                },
            },
            500: {
                "description": "Внутренняя ошибка сервера",
                "content": {
                    "application/json": {"example": {"error": "Internal server error."}}
                },
            },
        },
    ),
    "partner_import_schema": extend_schema(
        summary="Импорт данных поставщика",
        description="Эндпоинт для импорта данных поставщика. Возвращает ID задачи.",
        responses={
            200: {
                "description": "Задача на импорт данных поставлена в очередь",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Задача на импорт данных поставлена в очередь"
                        }
                    }
                },
            },
            400: {
                "description": "Пользователь не связан с магазином",
                "content": {
                    "application/json": {
                        "example": {"detail": "Вы не связаны с магазином."}
                    }
                },
            },
            401: {
                "description": "Пользователь не авторизован",
                "content": {
                    "application/json": {
                        "example": {"detail": "Пожалуйста, войдите в систему."}
                    }
                },
            },
            500: {
                "description": "Ошибка сервера",
                "content": {
                    "application/json": {
                        "example": {"error": "Ошибка при импорте данных: "}
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                value={"message": "Задача на импорт данных поставлена в очередь"},
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Ошибка: пользователь не связан с магазином",
                value={"detail": "Вы не связаны с магазином."},
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Ошибка: пользователь не авторизован",
                value={"detail": "Пожалуйста, войдите в систему."},
                status_codes=["401"],
            ),
            OpenApiExample(
                name="Ошибка сервера",
                value={"error": "Ошибка при импорте данных: "},
                status_codes=["500"],
            ),
        ],
    ),
    "check_partner_import_schema": extend_schema(
        summary="Проверка статуса задачи на импорт данных поставщика",
        description="Эндпоинт для проверки статуса задачи импорта. Возвращает текущий статус и результат выполнения.",
        responses={
            200: {
                "description": "Статус задачи",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "SUCCESS",
                            "data": {"message": "Данные успешно импортированы"},
                        }
                    }
                },
            },
            400: {
                "description": "Неверный формат task_id",
                "content": {
                    "application/json": {
                        "example": {"error": "Неверный формат идентификатора задачи"}
                    }
                },
            },
            401: {
                "description": "Пользователь не авторизован",
                "content": {
                    "application/json": {
                        "example": {"detail": "Пожалуйста, войдите в систему."}
                    }
                },
            },
            404: {
                "description": "Задача не найдена",
                "content": {
                    "application/json": {
                        "example": {"error": "Задача с указанным ID не найдена"}
                    }
                },
            },
            500: {
                "description": "Ошибка сервера",
                "content": {
                    "application/json": {
                        "example": {"error": "Внутренняя ошибка сервера"}
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешное выполнение",
                value={
                    "status": "SUCCESS",
                    "data": {"message": "Данные успешно импортированы"},
                },
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Задача в процессе",
                value={"status": "PENDING"},
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Ошибка выполнения",
                value={"status": "FAILURE", "error": "Ошибка валидации данных"},
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Неверный формат ID",
                value={"error": "Неверный формат идентификатора задачи"},
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Задача не найдена",
                value={"error": "Задача с указанным ID не найдена"},
                status_codes=["404"],
            ),
        ],
    ),
    "partner_orders_schema": extend_schema(
        summary="Получить подтвержденные заказы для партнера",
        description="Возвращает список подтвержденных заказов для магазина, связанного с текущим пользователем.",
        responses={
            200: {
                "description": "Список подтвержденных заказов",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Ошибка, если пользователь не связан с магазином.",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Список подтвержденных заказов",
                value=[{"id": 1, "status": "confirmed", "items": []}],
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Ошибка, если пользователь не связан с магазином",
                value={"detail": "User is not associated with a shop."},
                status_codes=["400"],
            ),
        ],
    ),
}
