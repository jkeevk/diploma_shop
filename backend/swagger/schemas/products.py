from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiExample,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import ProductSerializer

PRODUCT_ERROR_RESPONSES = {
    400: {"description": "Некорректные данные", "content": {"application/json": {}}},
    401: {"description": "Не авторизован", "content": {"application/json": {}}},
    403: {"description": "Доступ запрещен", "content": {"application/json": {}}},
    404: {"description": "Товар не найден", "content": {"application/json": {}}},
}

PRODUCT_VALIDATION_EXAMPLES = [
    OpenApiExample(
        name="Ошибка: обязательные поля",
        value={
            "name": ["Название товара обязательно для заполнения."],
            "category": ["Категория обязательна для заполнения."],
            "product_infos": ["Информация о продукте обязательна для заполнения."],
        },
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: несуществующий магазин",
        value={"product_infos": [{"shop": ["Неверный ID магазина."]}]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Неверные типы данных (запрос)",
        value={
            "name": {},
            "model": False,
            "category": [],
            "product_infos": [
                {
                    "shop": 1,
                    "external_id": [],
                    "description": [],
                    "quantity": -5,
                    "price": -5,
                    "price_rrc": "",
                    "parameters": {"parameter": False, "value": []},
                }
            ],
        },
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: неверные типы данных",
        value={
            "name": ["Некорректное название товара."],
            "model": ["Некорректная модель товара."],
            "category": ["Некорректное имя категории."],
            "product_infos": [
                {
                    "external_id": ["Некорректный внешний ID"],
                    "description": ["Некорректное описание"],
                    "quantity": ["Количество не может быть отрицательным."],
                    "price": ["Цена должна быть больше 0."],
                    "price_rrc": ["Некорректное число."],
                    "parameters": {
                        "parameter": ["Значение параметра должно быть строкой"],
                        "value": ["Значение параметра должно быть строкой"],
                    },
                }
            ],
        },
        status_codes=["400"],
        response_only=True,
    ),
]

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

NOT_FOUND_PRODUCT_EXAMPLE = OpenApiExample(
    name="Ошибка: товар не найден",
    value={"detail": "Товар не найден."},
    status_codes=["404"],
    response_only=True,
)

PRODUCT_EXAMPLE = {
    "id": 1,
    "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
    "model": "Updated Model",
    "category": "Телефоны",
    "product_infos": [
        {
            "shop": 1,
            "external_id": "142342",
            "description": "Познакомьтесь с iPhone XS 512 ГБ в золотом цвете в Apple Store — элегантный дизайн, высокая производительность и потрясающий Super Retina дисплей. Премиум-смартфон для тех, кто ценит лучшее!",
            "quantity": 14,
            "price": "110000.00",
            "price_rrc": "116990.00",
            "product_parameters": [
                {"parameter": "Встроенная память (Гб)", "value": "512"},
                {"parameter": "Диагональ (дюйм)", "value": "6.5"},
                {"parameter": "Разрешение (пикс)", "value": "2688x1242"},
                {"parameter": "Цвет", "value": "золотистый"},
            ],
        }
    ],
}

PRODUCT_SCHEMAS = {
    "product_viewset_schema": extend_schema_view(
        list=extend_schema(
            summary="Список товаров",
            description="Получение списка товаров с фильтрацией по магазину и категории.",
            parameters=[
                # Фильтрация
                OpenApiParameter(
                    name="category",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="Фильтр по ID категории",
                ),
                OpenApiParameter(
                    name="shop",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="Фильтр по ID магазина",
                ),
                # Пагинация
                OpenApiParameter(
                    name="limit",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="Количество результатов на странице (пагинация)",
                ),
                OpenApiParameter(
                    name="offset",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="Начальный индекс для пагинации",
                ),
                # Поиск
                OpenApiParameter(
                    name="search",
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    description="Поиск по названию, модели или категории",
                ),
            ],
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": PRODUCT_EXAMPLE}},
                },
                **{
                    k: v
                    for k, v in PRODUCT_ERROR_RESPONSES.items()
                    if k not in [400, 401, 403, 404]
                },
            },
            examples=[
                OpenApiExample(
                    name="Фильтр по магазину",
                    value=PRODUCT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Пустой результат",
                    value=[],
                    status_codes=["200"],
                    response_only=True,
                ),
            ],
        ),
        create=extend_schema(
            summary="Создать товар",
            description="Создание товара с привязкой к магазинам. Требуются права администратора или поставщика.",
            request=ProductSerializer,
            responses={
                201: {
                    "description": "Товар создан",
                    "content": {"application/json": {"example": PRODUCT_EXAMPLE}},
                },
                **{k: v for k, v in PRODUCT_ERROR_RESPONSES.items() if k != 404},
            },
            examples=[
                OpenApiExample(
                    name="Успешный запрос",
                    value={
                        "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
                        "model": "Updated Model",
                        "category": "Телефоны",
                        "product_infos": [
                            {
                                "shop": 1,
                                "description": "Познакомьтесь с iPhone XS 512 ГБ в золотом цвете в Apple Store — элегантный дизайн, высокая производительность и потрясающий Super Retina дисплей. Премиум-смартфон для тех, кто ценит лучшее!",
                                "external_id": 142342,
                                "quantity": 14,
                                "price": "110000.00",
                                "price_rrc": "116990.00",
                                "parameters": {
                                    "Встроенная память (Гб)": "512",
                                    "Диагональ (дюйм)": "6.5",
                                    "Разрешение (пикс)": "2688x1242",
                                    "Цвет": "золотистый",
                                },
                            }
                        ],
                    },
                    status_codes=["201"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=PRODUCT_EXAMPLE,
                    status_codes=["201"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Только обязательные поля (запрос)",
                    value={
                        "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
                        "category": "Телефоны",
                        "product_infos": [{"shop": 1, "price": "110000.00"}],
                    },
                    status_codes=["201"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Только обязательные поля (ответ)",
                    value={
                        "id": 1,
                        "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
                        "model": "",
                        "category": "Телефоны",
                        "product_infos": [
                            {
                                "shop": 1,
                                "external_id": None,
                                "description": "",
                                "quantity": 0,
                                "price": "110000.00",
                                "price_rrc": None,
                                "product_parameters": [],
                            }
                        ],
                    },
                    status_codes=["201"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Пустые поля (запрос)",
                    value={},
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: Пустые поля",
                    value={
                        "name": ["Название товара обязательно для заполнения."],
                        "category": ["Категория обязательна для заполнения."],
                        "product_infos": [
                            "Информация о продукте обязательна для заполнения."
                        ],
                    },
                    status_codes=["400"],
                    response_only=True,
                ),
                *AUTH_ERROR_EXAMPLES,
                *PRODUCT_VALIDATION_EXAMPLES,
            ],
        ),
        retrieve=extend_schema(
            summary="Получить товар",
            description="Детальная информация о товаре по ID.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    required=True,
                    description="ID товара",
                )
            ],
            responses={
                200: {"content": {"application/json": {"example": PRODUCT_EXAMPLE}}},
                **{
                    k: v
                    for k, v in PRODUCT_ERROR_RESPONSES.items()
                    if k not in [400, 401, 403]
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=PRODUCT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_PRODUCT_EXAMPLE,
            ],
        ),
        update=extend_schema(
            summary="Обновить товар",
            description="Полное обновление данных товара (включая product_infos). Требуются права администратора или поставщика.",
            request=ProductSerializer,
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    required=True,
                    description="ID товара",
                )
            ],
            responses={
                200: {"content": {"application/json": {"example": PRODUCT_EXAMPLE}}},
                **PRODUCT_ERROR_RESPONSES,
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=PRODUCT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Обновление магазина",
                    value={
                        "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
                        "model": "Updated Model",
                        "category": "Телефоны",
                        "product_infos": [
                            {
                                "shop": 1,
                                "quantity": 14,
                                "price": "110000.00",
                                "price_rrc": "116990.00",
                                "parameters": {
                                    "Встроенная память (Гб)": "512",
                                    "Диагональ (дюйм)": "6.5",
                                    "Разрешение (пикс)": "2688x1242",
                                    "Цвет": "золотистый",
                                },
                            }
                        ],
                    },
                    status_codes=["200"],
                    request_only=True,
                ),
                *PRODUCT_VALIDATION_EXAMPLES,
                NOT_FOUND_PRODUCT_EXAMPLE,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        partial_update=extend_schema(
            summary="Частичное обновление",
            description="Изменение отдельных полей товара. Требуются права администратора или поставщика.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    required=True,
                    description="ID товара",
                )
            ],
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=PRODUCT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Обновление модели",
                    value={"model": "Updated Model"},
                    status_codes=["200"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Обновление цены и количества товара",
                    value={"product_infos": [{"quantity": 120, "price": 129000}]},
                    status_codes=["200"],
                    request_only=True,
                ),
                *AUTH_ERROR_EXAMPLES,
                *PRODUCT_VALIDATION_EXAMPLES[1:],
                NOT_FOUND_PRODUCT_EXAMPLE,
            ],
            responses={
                200: {"content": {"application/json": {"example": PRODUCT_EXAMPLE}}},
                **PRODUCT_ERROR_RESPONSES,
            },
        ),
        destroy=extend_schema(
            summary="Удалить товар",
            description="Удаление товара. Требуются права администратора или поставщика.",
            responses={
                204: {"description": "Товар удален"},
                **{k: v for k, v in PRODUCT_ERROR_RESPONSES.items() if k != 400},
            },
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    required=True,
                    description="ID товара",
                )
            ],
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=None,
                    status_codes=["204"],
                    response_only=True,
                ),
                NOT_FOUND_PRODUCT_EXAMPLE,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
    )
}
