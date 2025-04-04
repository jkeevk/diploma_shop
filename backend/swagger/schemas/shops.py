from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import ShopSerializer


SHOP_SCHEMAS = {
    "shop_schema": extend_schema_view(
        get=extend_schema(
            description="Получить список всех магазинов.",
            summary="Список магазинов",
            tags=["Магазины"],
            responses={
                200: {
                    "description": "Некорректные данные",
                    "content": {"application/json": {}},
                }
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value={
                        "id": 1,
                        "name": "TechShop",
                        "url": "https://example.com",
                    },
                    status_codes=["200"],
                    response_only=True,
                )
            ],
        ),
        post=extend_schema(
            description="Создать новый магазин и связать его с текущим пользователем. Только пользователи с ролью admin или supplier могут выполнять этот запрос.",
            summary="Создание магазина",
            tags=["Магазины"],
            request=ShopSerializer,
            responses={
                201: ShopSerializer,
                400: {
                    "description": "Некорректные данные",
                    "content": {"application/json": {}},
                },
                401: {
                    "description": "Не авторизован",
                    "content": {"application/json": {}},
                },
                403: {
                    "description": "Доступ запрещен",
                    "content": {"application/json": {}},
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value={
                        "id": 1,
                        "name": "TechShop",
                        "url": "https://example.com",
                    },
                    status_codes=["201"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Успешный запрос для администратора",
                    value={"name": "TechShop", "url": "https://example.com", "user": 1},
                    status_codes=["201"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный запрос для продавца",
                    value={
                        "name": "TechShop",
                        "url": "https://example.com",
                    },
                    status_codes=["201"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: указание пользователя продавцом",
                    value={
                        "user": [
                            "Указание пользователя доступно только администраторам."
                        ]
                    },
                    status_codes=["400"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: невалидные данные",
                    value={
                        "name": ["Некорректное название магазина"],
                        "url": ["Введите корректный URL-адрес"],
                    },
                    status_codes=["400"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: магазин привязан (запрос продавца)",
                    value={
                        "name": "Магазин с таким названием уже существует у другого продавца"
                    },
                    status_codes=["400"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: магазин уже существует",
                    value={"name": "Магазин с таким названием уже существует"},
                    status_codes=["400"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: невалидные данные",
                    value={"name": [], "url": "https://3"},
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: обязательные поля",
                    value={"url": "https://example.com/"},
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: обязательные поля",
                    value={"name": ["Обязательное поле"]},
                    status_codes=["400"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: пользователь не авторизован",
                    value={"detail": "Пожалуйста, войдите в систему."},
                    status_codes=["401"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: доступ запрещен",
                    value={
                        "detail": "У вас недостаточно прав для выполнения этого действия."
                    },
                    status_codes=["403"],
                    response_only=True,
                ),
            ],
        ),
    )
}
