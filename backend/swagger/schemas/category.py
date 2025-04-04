from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import CategorySerializer

CATEGORY_ERROR_RESPONSES = {
    400: {"description": "Некорректные данные", "content": {"application/json": {}}},
    401: {"description": "Не авторизован", "content": {"application/json": {}}},
    403: {"description": "Доступ запрещен", "content": {"application/json": {}}},
    404: {"description": "Категория не найдена", "content": {"application/json": {}}},
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

CATEGORY_EXAMPLE = {"id": 1, "name": "Электроника"}

VALIDATION_EXAMPLES = [
    OpenApiExample(
        name="Ошибка: пустое имя категории",
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
        name="Ошибка: дубликат категории",
        value={"name": ["Категория с таким именем уже существует."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: некорректные данные (запрос)",
        value={"name": [1, 3, "Категория"]},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: некорректные данные",
        value={"name": ["Имя категории должно быть строкой"]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение категории (запрос)",
        value={"name": ""},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение категории",
        value={"name": ["Имя категории не может быть пустым"]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение (null) категории (запрос)",
        value={"name": None},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое значение (null) категории",
        value={"name": ["Категория не может быть пустой"]},
        status_codes=["400"],
        response_only=True,
    ),
]

NOT_FOUND_EXAMPLE = OpenApiExample(
    name="Ошибка: категория не найдена",
    value={"detail": "Категория не найдена"},
    status_codes=["404"],
    response_only=True,
)

CATEGORY_SCHEMAS = {
    "category_viewset_schema": extend_schema_view(
        list=extend_schema(
            summary="Список категорий",
            description="Получение списка всех категорий с возможностью фильтрации по названию. Авторизация не требуется.",
            tags=["Категории"],
            parameters=[
                OpenApiParameter(
                    name="name",
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    description="Фильтр по названию категории (частичное совпадение, без учета регистра)",
                ),
            ],
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": [CATEGORY_EXAMPLE]}},
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=[CATEGORY_EXAMPLE],
                    status_codes=["200"],
                    response_only=True,
                )
            ],
        ),
        create=extend_schema(
            summary="Создать категорию",
            description="Создание новой категории. Требуются права администратора.",
            tags=["Категории"],
            request=CategorySerializer,
            responses={
                201: {
                    "description": "Категория создана",
                    "content": {"application/json": {"example": CATEGORY_EXAMPLE}},
                },
                **{k: v for k, v in CATEGORY_ERROR_RESPONSES.items() if k != 404},
            },
            examples=[
                OpenApiExample(
                    name="Успешный запрос",
                    value={"name": "Новая категория"},
                    status_codes=["201"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=CATEGORY_EXAMPLE,
                    status_codes=["201"],
                    response_only=True,
                ),
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        retrieve=extend_schema(
            summary="Получить категорию",
            description="Получение информации о категории по ID. Авторизация не требуется.",
            tags=["Категории"],
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID категории",
                    required=True,
                )
            ],
            responses={
                200: {
                    "description": "Успешный ответ",
                    "content": {"application/json": {"example": CATEGORY_EXAMPLE}},
                },
                **{k: v for k, v in CATEGORY_ERROR_RESPONSES.items() if k in [404]},
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    value=CATEGORY_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
            ],
        ),
        update=extend_schema(
            summary="Обновить категорию",
            description="Полное обновление категории. Требуются права администратора.",
            tags=["Категории"],
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID категории",
                    required=True,
                )
            ],
            request=CategorySerializer,
            responses={
                200: {
                    "description": "Категория обновлена",
                    "content": {"application/json": {"example": CATEGORY_EXAMPLE}},
                },
                **CATEGORY_ERROR_RESPONSES,
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
                    value=CATEGORY_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
                *VALIDATION_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        partial_update=extend_schema(
            summary="Частично обновить категорию",
            description="Частичное обновление категории. Поля, которые не переданы в запросе, останутся прежними.",
            tags=["Категории"],
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID категории",
                    required=True,
                )
            ],
            request=CategorySerializer,
            responses={
                200: {
                    "description": "Категория обновлена",
                    "content": {"application/json": {"example": CATEGORY_EXAMPLE}},
                },
                **CATEGORY_ERROR_RESPONSES,
            },
            examples=[
                OpenApiExample(
                    name="Успешный запрос",
                    value={"name": "Частичное обновление"},
                    status_codes=["200"],
                    request_only=True,
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    value=CATEGORY_EXAMPLE,
                    status_codes=["200"],
                    response_only=True,
                ),
                NOT_FOUND_EXAMPLE,
                *VALIDATION_EXAMPLES[2:],
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        destroy=extend_schema(
            summary="Удалить категорию",
            description="Удаление категории. Требуются права администратора. Связанные товары будут удалены.",
            tags=["Категории"],
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID категории",
                    required=True,
                )
            ],
            responses={
                204: {"description": "Категория удалена"},
                **{k: v for k, v in CATEGORY_ERROR_RESPONSES.items() if k != 400},
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
