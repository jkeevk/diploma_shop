from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)

COMMON_ERROR_RESPONSES = {
    401: {
        "description": "Пользователь не авторизован",
        "content": {"application/json": {}},
    },
    403: {
        "description": "Доступ запрещен",
        "content": {"application/json": {}},
    },
    404: {
        "description": "Элемент не найден",
        "content": {"application/json": {}},
    },
}

COMMON_ERROR_EXAMPLES = [
    OpenApiExample(
        name="Ошибка авторизации",
        value={"detail": "Пожалуйста, войдите в систему."},
        response_only=True,
        status_codes=["401"],
    ),
    OpenApiExample(
        name="Ошибка доступа",
        value={"detail": "У вас недостаточно прав для выполнения этого действия."},
        response_only=True,
        status_codes=["403"],
    ),
    OpenApiExample(
        name="Элемент не найден",
        value={"detail": "Корзина не найдена."},
        response_only=True,
        status_codes=["404"],
    ),
]

VALIDATION_ERROR_EXAMPLES = [
    OpenApiExample(
        name="Нет товаров в заказе",
        value={"order_items": ["Обязательное поле"]},
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Магазин не привязан к пользователю",
        value=["Магазин Books World не привязан к пользователю"],
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Недостаточно товара",
        value=[
            "Недостаточно товара Python Basics (ID=3) в магазине Books World (ID=1). Доступно: 5, запрошено: 10."
        ],
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Некорректный статус",
        value={
            "detail": "Некорректный статус: test. Доступные статусы: new, confirmed, assembled, sent, delivered, canceled"
        },
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Недостаточно прав для изменения статуса",
        value={
            "detail": "Недостаточно прав. Вы можете устанавливать только: new, canceled"
        },
        response_only=True,
        status_codes=["400"],
    ),
]

BASKET_SUCCESS_EXAMPLES = [
    OpenApiExample(
        name="Успешный ответ",
        value={
            "id": 1,
            "user": 1,
            "order_items": [{"id": 1, "product": 1, "shop": 1, "quantity": 2}],
            "dt": "2025-03-26T21:32:57.257443Z",
            "status": "new",
        },
        response_only=True,
        status_codes=["200"],
    ),
    OpenApiExample(
        name="Пустая корзина",
        value=[],
        response_only=True,
        status_codes=["200"],
    ),
]

CREATE_BASKET_EXAMPLES = [
    OpenApiExample(
        name="Успешный запрос",
        value={
            "user": 1,
            "order_items": [{"product": 3, "shop": 1, "quantity": 5}],
        },
        request_only=True,
        status_codes=["201"],
    ),
    OpenApiExample(
        name="Корзина успешно создана",
        value={
            "id": 7,
            "user": 1,
            "order_items": [{"id": 46, "product": 1, "shop": 1, "quantity": 1}],
            "dt": "2025-03-27T16:22:18.768645Z",
            "status": "new",
        },
        response_only=True,
        status_codes=["201"],
    ),
]

CONFIRM_BASKET_EXAMPLES = [
    OpenApiExample(
        name="Успешное подтверждение",
        value={"detail": "Заказ успешно подтвержден."},
        response_only=True,
        status_codes=["200"],
    ),
    OpenApiExample(
        name="Пустая корзина",
        value={"non_field_errors": ["Корзина пуста."]},
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Отсутствует contact_id",
        value={"contact_id": ["ID контакта обязателен."]},
        response_only=True,
        status_codes=["400"],
    ),
]

BASKET_SCHEMAS = {
    "basket_viewset_schema": extend_schema_view(
        list=extend_schema(
            summary="Список активных корзин",
            description="Возвращает список активных корзин с заказами пользователя. Требуется авторизация и права покупателя.",
            responses={
                200: {
                    "description": "Список активных корзин пользователя",
                    "content": {"application/json": {}},
                },
                **COMMON_ERROR_RESPONSES,
            },
            examples=[*BASKET_SUCCESS_EXAMPLES, *COMMON_ERROR_EXAMPLES],
        ),
        create=extend_schema(
            summary="Создать новую корзину",
            description="Создает новую корзину для пользователя. Требуется авторизация и права покупателя.",
            responses={
                201: {
                    "description": "Корзина успешно создана",
                    "content": {"application/json": {}},
                },
                400: {
                    "description": "Ошибки валидации",
                    "content": {"application/json": {}},
                },
                **COMMON_ERROR_RESPONSES,
            },
            examples=[
                *CREATE_BASKET_EXAMPLES,
                *VALIDATION_ERROR_EXAMPLES,
                *COMMON_ERROR_EXAMPLES,
            ],
        ),
        retrieve=extend_schema(
            summary="Получить корзину по ID",
            description="Возвращает корзину по указанному ID. Требуется авторизация и права покупателя.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                200: {
                    "description": "Корзина найдена",
                    "content": {"application/json": {}},
                },
                **COMMON_ERROR_RESPONSES,
            },
            examples=[*BASKET_SUCCESS_EXAMPLES[:1], *COMMON_ERROR_EXAMPLES],
        ),
        update=extend_schema(
            summary="Обновить корзину по ID",
            description="Обновляет корзину по указанному ID. Требуется авторизация.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                200: {
                    "description": "Корзина успешно обновлена",
                    "content": {"application/json": {}},
                },
                400: {
                    "description": "Ошибки валидации",
                    "content": {"application/json": {}},
                },
                **COMMON_ERROR_RESPONSES,
            },
            examples=[
                *BASKET_SUCCESS_EXAMPLES[:1],
                *VALIDATION_ERROR_EXAMPLES,
                *COMMON_ERROR_EXAMPLES,
            ],
        ),
        partial_update=extend_schema(
            summary="Частичное обновление корзины",
            description="Частично обновляет корзину. Требуется авторизация.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                200: {
                    "description": "Корзина успешно обновлена",
                    "content": {"application/json": {}},
                },
                400: {
                    "description": "Ошибки валидации",
                    "content": {"application/json": {}},
                },
                **COMMON_ERROR_RESPONSES,
            },
            examples=[
                OpenApiExample(
                    name="Успешное частичное обновление",
                    value={"order_items": [{"product": 1, "quantity": 2}]},
                    request_only=True,
                    status_codes=["200"],
                ),
                *BASKET_SUCCESS_EXAMPLES[:1],
                *VALIDATION_ERROR_EXAMPLES,
                *COMMON_ERROR_EXAMPLES,
            ],
        ),
        destroy=extend_schema(
            summary="Удалить корзину по ID",
            description="Удаляет корзину по указанному ID. Требуется авторизация.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                204: {
                    "description": "Корзина успешно удалена",
                    "content": {"application/json": {}},
                },
                **COMMON_ERROR_RESPONSES,
            },
            examples=[
                OpenApiExample(
                    name="Корзина успешно удалена",
                    value=[],
                    response_only=True,
                    status_codes=["204"],
                ),
                *COMMON_ERROR_EXAMPLES,
            ],
        ),
    ),
    "confirm_basket_schema": extend_schema(
        summary="Подтвердить корзину",
        description="Подтвердить заказ. Изменяет статус корзины на 'подтвержден'.",
        parameters=[
            OpenApiParameter(
                name="contact_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID контакта пользователя в системе",
            ),
        ],
        responses={
            200: {
                "description": "Корзина успешно подтверждена",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Ошибки валидации",
                "content": {"application/json": {}},
            },
            **COMMON_ERROR_RESPONSES,
        },
        examples=[*CONFIRM_BASKET_EXAMPLES, *COMMON_ERROR_EXAMPLES],
    ),
}
