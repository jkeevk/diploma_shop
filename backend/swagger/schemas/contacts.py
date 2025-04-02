from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiExample,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import ContactSerializer

CONTACT_ERROR_RESPONSES = {
    400: {"description": "Некорректные данные", "content": {"application/json": {}}},
    401: {"description": "Не авторизован", "content": {"application/json": {}}},
    403: {"description": "Доступ запрещен", "content": {"application/json": {}}},
    404: {"description": "Контакт не найден", "content": {"application/json": {}}},
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

VALIDATION_EXAMPLES = [
    OpenApiExample(
        name="Ошибка: обязательные поля",
        value={
            "user": ["Пользователь обязателен для заполнения"],
            "city": ["Город обязателен для заполнения"],
            "street": ["Улица обязательна для заполнения"],
            "house": ["Дом обязателен для заполнения"],
            "phone": ["Телефон обязателен для заполнения"],
        },
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: некорректный пользователь",
        value={"user": ["Пользователь с ID 999 не существует"]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: некорректные типы данных",
        value={
            "phone": ["Телефон не может быть пустым"],
            "house": ["Некорректный номер дома"],
            "structure": ["Некорректный номер корпуса"],
        },
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: неверный формат телефона",
        value={"phone": ["Введите корректный номер телефона в формате +79991234567"]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: чужой пользователь",
        value={"user": ["Вы не можете указывать другого пользователя."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: максимум контактов",
        value={"non_field_errors": ["Максимум 5 адресов на пользователя."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: null-значения",
        value={
            "city": ["Город не может быть пустым"],
            "street": ["Улица не может быть пустой"],
            "house": ["Дом не может быть пустым"],
        },
        status_codes=["400"],
        response_only=True,
    ),
]

NOT_FOUND_EXAMPLE = OpenApiExample(
    name="Ошибка: контакт не найден",
    value={"detail": "Контакт не найден."},
    status_codes=["404"],
    response_only=True,
)

CONTACT_EXAMPLE = {
    "id": 1,
    "city": "Москва",
    "street": "Ленина",
    "house": "42",
    "structure": "1",
    "building": "А",
    "apartment": "123",
    "phone": "+79991234567",
    "user": 1,
}

CONTACT_SCHEMAS = {
    "contact_viewset_schema": extend_schema_view(
        list=extend_schema(
            summary="Список контактов",
            description="Получение списка всех контактов. Администраторы видят все контакты.",
            parameters=[
                OpenApiParameter(
                    name="user",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="Фильтр по ID пользователя (только для администраторов)",
                )
            ],
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": [CONTACT_EXAMPLE]}},
                },
                **{
                    k: v
                    for k, v in CONTACT_ERROR_RESPONSES.items()
                    if k in [400, 401, 403]
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=[CONTACT_EXAMPLE],
                    status_codes=["200"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: некорректный фильтр",
                    value={"user": ["Недопустимый ID пользователя"]},
                    status_codes=["400"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка доступа к фильтру",
                    value={
                        "detail": "Фильтрация по пользователю доступна только администраторам"
                    },
                    status_codes=["403"],
                    response_only=True,
                ),
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        create=extend_schema(
            summary="Создать контакт",
            description="Добавление нового контактного адреса. Требуются права администратора.",
            request=ContactSerializer,
            responses={
                201: {
                    "description": "Контакт создан",
                    "content": {"application/json": {"example": CONTACT_EXAMPLE}},
                },
                **{k: v for k, v in CONTACT_ERROR_RESPONSES.items() if k != 404},
            },
            examples=[
                # Успешные примеры
                OpenApiExample(
                    name="Успешный запрос",
                    value={k: v for k, v in CONTACT_EXAMPLE.items() if k != "id"},
                    status_codes=["201"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=CONTACT_EXAMPLE,
                    status_codes=["201"],
                    response_only=True,
                ),
                # Примеры ошибок запросов
                OpenApiExample(
                    name="Ошибка: пустой запрос",
                    value={},
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: null-значения",
                    value={
                        "city": None,
                        "street": None,
                        "house": None,
                        "phone": None,
                        "user": None,
                    },
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: неверные типы данных",
                    value={
                        "city": 123,
                        "street": ["ул. Ленина"],
                        "house": {"number": 42},
                        "phone": [],
                        "user": "admin",
                    },
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: пустые строки",
                    value={
                        "city": "",
                        "street": "   ",
                        "house": "",
                        "phone": "",
                        "user": 1,
                    },
                    status_codes=["400"],
                    request_only=True,
                ),
                # Примеры ответов
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        retrieve=extend_schema(
            summary="Получить контакт",
            description="Получение информации о контакте по ID.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID контакта",
                    required=True,
                )
            ],
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": CONTACT_EXAMPLE}},
                },
                **{k: v for k, v in CONTACT_ERROR_RESPONSES.items() if k in [404]},
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=CONTACT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
            ],
        ),
        update=extend_schema(
            summary="Обновить контакт",
            description="Полное обновление контактных данных. Требуются права администратора.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID контакта",
                    required=True,
                )
            ],
            request=ContactSerializer,
            responses={
                200: {
                    "description": "Контакт обновлен",
                    "content": {"application/json": {"example": CONTACT_EXAMPLE}},
                },
                **CONTACT_ERROR_RESPONSES,
            },
            examples=[
                # Успешные примеры
                OpenApiExample(
                    name="Успешный запрос",
                    value={k: v for k, v in CONTACT_EXAMPLE.items() if k != "id"},
                    status_codes=["200"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=CONTACT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                # Примеры ошибок запросов
                OpenApiExample(
                    name="Ошибка: частичный запрос",
                    value={"city": "СПб"},
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: неверный ID пользователя",
                    value={"user": "admin"},
                    status_codes=["400"],
                    request_only=True,
                ),
                # Примеры ответов
                NOT_FOUND_EXAMPLE,
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        partial_update=extend_schema(
            summary="Частично обновить контакт",
            description="Частичное обновление контактных данных.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID контакта",
                    required=True,
                )
            ],
            request=ContactSerializer,
            responses={
                200: {
                    "description": "Контакт обновлен",
                    "content": {"application/json": {"example": CONTACT_EXAMPLE}},
                },
                **CONTACT_ERROR_RESPONSES,
            },
            examples=[
                # Успешные примеры
                OpenApiExample(
                    name="Успешный запрос",
                    value={"phone": "+79998765432"},
                    status_codes=["200"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=CONTACT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                # Примеры ошибок запросов
                OpenApiExample(
                    name="Ошибка: пустой запрос",
                    value={},
                    status_codes=["400"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: неверный тип телефона",
                    value={"phone": [1234567]},
                    status_codes=["400"],
                    request_only=True,
                ),
                # Примеры ответов
                NOT_FOUND_EXAMPLE,
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        destroy=extend_schema(
            summary="Удалить контакт",
            description="Удаление контактного адреса. Требуются права администратора.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID контакта",
                    required=True,
                )
            ],
            responses={
                204: {"description": "Контакт удален"},
                **{k: v for k, v in CONTACT_ERROR_RESPONSES.items() if k != 400},
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=None,
                    status_codes=["204"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
    )
}
