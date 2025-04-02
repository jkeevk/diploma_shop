from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiExample,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import ParameterSerializer

PARAMETER_ERROR_RESPONSES = {
    400: {"description": "Некорректные данные", "content": {"application/json": {}}},
    401: {"description": "Не авторизован", "content": {"application/json": {}}},
    403: {"description": "Доступ запрещен", "content": {"application/json": {}}},
    404: {"description": "Параметр не найден", "content": {"application/json": {}}},
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

PARAMETER_EXAMPLE = {"id": 1, "name": "Цвет"}

VALIDATION_EXAMPLES = [
    OpenApiExample(
        name="Ошибка: пустое имя параметра",
        value={"name": ["Это поле обязательно."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение (запрос)",
        value={},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: дубликат параметра",
        value={"name": ["Параметр с таким именем уже существует."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: некорректные данные (запрос)",
        value={"name": [1, 3, "Цвет"]},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение параметра(запрос)",
        value={"name": ""},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение параметра(запрос)",
        value={"name": ["Имя параметра не может быть пустым"]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение (null) параметра(запрос)",
        value={"name": None},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение (null) параметра",
        value={"name": ["Параметр не может быть пустым"]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: некорректный тип данных (ответ)",
        value={"name": ["Имя параметра должно быть строкой"]},
        status_codes=["400"],
        response_only=True,
    ),
]

NOT_FOUND_EXAMPLE = OpenApiExample(
    name="Ошибка: параметр не найден",
    value={"detail": "Параметр не найден."},
    status_codes=["404"],
    response_only=True,
)

PARAMETER_SCHEMAS = {
    "parameter_viewset_schema": extend_schema_view(
        list=extend_schema(
            summary="Список параметров",
            description="Получение списка всех параметров товаров. Требуются права администратора или поставщика.",
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": PARAMETER_EXAMPLE}},
                },
                **{
                    k: v
                    for k, v in PARAMETER_ERROR_RESPONSES.items()
                    if k not in [400, 404]
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=PARAMETER_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        create=extend_schema(
            summary="Создать параметр",
            description="Создание нового параметра товара. Требуются права администратора или поставщика.",
            request=ParameterSerializer,
            responses={
                201: {
                    "description": "Параметр создан",
                    "content": {"application/json": {"example": PARAMETER_EXAMPLE}},
                },
                **{
                    k: v for k, v in PARAMETER_ERROR_RESPONSES.items() if k not in [404]
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный запрос",
                    value={"name": "Цвет"},
                    status_codes=["201"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=PARAMETER_EXAMPLE,
                    status_codes=["201"],
                    response_only=True,
                ),
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        retrieve=extend_schema(
            summary="Получить параметр",
            description="Получение информации о параметре по ID. Требуются права администратора или поставщика.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID параметра",
                    required=True,
                )
            ],
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": PARAMETER_EXAMPLE}},
                },
                **{
                    k: v for k, v in PARAMETER_ERROR_RESPONSES.items() if k not in [400]
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=PARAMETER_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        update=extend_schema(
            summary="Обновить параметр",
            description="Полное обновление параметра. Требуются права администратора или поставщика.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID параметра",
                    required=True,
                )
            ],
            request=ParameterSerializer,
            responses={
                200: {
                    "description": "Параметр обновлен",
                    "content": {"application/json": {"example": PARAMETER_EXAMPLE}},
                },
                **PARAMETER_ERROR_RESPONSES,
            },
            examples=[
                OpenApiExample(
                    name="Успешный запрос",
                    value={"name": "Новое название"},
                    status_codes=["200"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=PARAMETER_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        partial_update=extend_schema(
            summary="Частично обновить параметр",
            description="Частичное обновление параметра. Поля, которые не переданы в запросе, останутся прежними.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID параметра",
                    required=True,
                )
            ],
            request=ParameterSerializer,
            responses={
                200: {
                    "description": "Параметр обновлен",
                    "content": {"application/json": {"example": PARAMETER_EXAMPLE}},
                },
                **PARAMETER_ERROR_RESPONSES,
            },
            examples=[
                OpenApiExample(
                    name="Успешный запрос",
                    value={"name": "Обновленное название"},
                    status_codes=["200"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=PARAMETER_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
                *VALIDATION_EXAMPLES[2:],
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        destroy=extend_schema(
            summary="Удалить параметр",
            description="Удаление параметра. Требуются права администратора или поставщика.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID параметра",
                    required=True,
                )
            ],
            responses={
                204: {"description": "Параметр удален"},
                **{
                    k: v for k, v in PARAMETER_ERROR_RESPONSES.items() if k not in [400]
                },
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
