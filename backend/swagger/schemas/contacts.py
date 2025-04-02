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

VALIDATION_EXAMPLES = [
    OpenApiExample(
        name="Ошибка валидации",
        value={"phone": ["Enter a valid value."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: обязательное поле",
        value={"user": ["This field is required."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: чужой пользователь",
        value={"user": ["Вы не можете указывать другого пользователя."]},
        status_codes=["400"],
        response_only=True,
    ),
]

COMBINED_ERROR_EXAMPLE_REQUEST = OpenApiExample(
    name="Ошибка: комбинированная ошибка",
    value={
        "city": None,
        "street": None,
        "house": None,
        "structure": None,
        "building": None,
        "apartment": None,
        "phone": "1",
        "user": 999,
    },
    status_codes=["400"],
    request_only=True,
)

COMBINED_ERROR_EXAMPLE_RESPONSE = OpenApiExample(
    name="Ошибка: комбинированная ошибка",
    value={
        "city": ["This field may not be None."],
        "street": ["This field may not be None."],
        "house": ["This field may not be None."],
        "structure": ["This field may not be None."],
        "building": ["This field may not be None."],
        "apartment": ["This field may not be None."],
        "phone": ["Enter a valid value."],
        "user": ['Invalid pk "999" - object does not exist.'],
    },
    status_codes=["400"],
    response_only=True,
)

NOT_FOUND_EXAMPLE = OpenApiExample(
    name="Ошибка: контакт не найден",
    value={"detail": "No Contact matches the given query."},
    status_codes=["404"],
    response_only=True,
)

CONTACT_SCHEMAS = {
    "contact_viewset_schema": extend_schema_view(
        list=extend_schema(
            summary="Получить контакты",
            description="Список контактов пользователя. Администраторы видят все контакты.",
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": [CONTACT_EXAMPLE]}},
                },
                **{
                    k: v
                    for k, v in CONTACT_ERROR_RESPONSES.items()
                    if k not in [400, 404]
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=CONTACT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        create=extend_schema(
            summary="Создать контакт",
            description="Добавление нового контактного адреса.",
            request=ContactSerializer,
            responses={
                201: {
                    "description": "Контакт создан",
                    "content": {"application/json": {"example": CONTACT_EXAMPLE}},
                },
                **CONTACT_ERROR_RESPONSES,
            },
            examples=[
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
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        retrieve=extend_schema(
            summary="Получить контакт",
            description="Детальная информация о контакте.",
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
                    "content": {"application/json": {"example": [CONTACT_EXAMPLE]}},
                },
                **{k: v for k, v in CONTACT_ERROR_RESPONSES.items() if k not in [400]},
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=CONTACT_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        update=extend_schema(
            summary="Обновить контакт",
            description="Полное обновление контактных данных.",
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
                NOT_FOUND_EXAMPLE,
                *VALIDATION_EXAMPLES,
                COMBINED_ERROR_EXAMPLE_REQUEST,
                COMBINED_ERROR_EXAMPLE_RESPONSE,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        partial_update=extend_schema(
            summary="Частично обновить",
            description="Обновление отдельных полей контакта. Поля, которые не переданы в запросе, останутся прежними.",
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
                NOT_FOUND_EXAMPLE,
                OpenApiExample(
                    name="Ошибка: некорректные данные",
                    value={"phone": ["Enter a valid value."]},
                    status_codes=["400"],
                    response_only=True,
                ),
                COMBINED_ERROR_EXAMPLE_REQUEST,
                COMBINED_ERROR_EXAMPLE_RESPONSE,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        destroy=extend_schema(
            summary="Удалить контакт",
            description="Удаление контактного адреса.",
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
                204: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": [CONTACT_EXAMPLE]}},
                },
                **{k: v for k, v in CONTACT_ERROR_RESPONSES.items() if k not in [400]},
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
