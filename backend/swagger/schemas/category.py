from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import CategorySerializer

AUTH_ERROR_RESPONSES = {
    400: {
        "description": "Некорректные данные",
        "content": {"application/json": {}},
    },
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

CRUD_ERROR_EXAMPLES = [
    OpenApiExample(
        name="Ошибка: категория с таким именем уже существует",
        value={"name": ["Категория with this Название already exists."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: обязательное поле",
        value={},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: обязательное поле",
        value={"name": ["This field is required."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое поле",
        value={"name": None},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: пустое поле",
        value={"name": ["This field may not be null."]},
        status_codes=["400"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: невалидное поле",
        value={"name": [1, 3]},
        status_codes=["400"],
        request_only=True,
    ),
    OpenApiExample(
        name="Ошибка: невалидное поле",
        value={"name": ["Not a valid string."]},
        status_codes=["400"],
        response_only=True,
    ),
]


CATEGORY_SCHEMAS = {
    "category_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех категорий. Фильтрация возможна по названию. Авторизация не требуется.",
            summary="Список категорий",
            responses={200: CategorySerializer(many=True)},
            parameters=[
                OpenApiParameter(
                    name="name",
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    description="Фильтр по названию категории (частичное совпадение, без учета регистра)",
                ),
                OpenApiParameter(
                    name="limit",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="Количество результатов на странице",
                ),
                OpenApiParameter(
                    name="offset",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                    description="Начальная позиция в списке результатов",
                ),
            ],
        ),
        create=extend_schema(
            description="Создать новую категорию. Только администратор может создавать категории.",
            summary="Создание категории",
            request=CategorySerializer,
            responses={201: CategorySerializer, **AUTH_ERROR_RESPONSES},
            examples=[
                OpenApiExample(
                    name="Успешное создание категории",
                    value={"id": 1, "name": "Category name"},
                    status_codes=["201"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Успешное создание категории",
                    value={"name": "Category name"},
                    status_codes=["201"],
                    request_only=True,
                ),
                *CRUD_ERROR_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        retrieve=extend_schema(
            description="Получить информацию о категории по её ID. Авторизация не требуется.",
            summary="Получение категории по ID",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="Уникальный идентификатор категории (целое число)",
                    required=True,
                ),
            ],
            responses={
                200: {
                    "description": "Список категорий",
                    "content": {"application/json": {}},
                },
                404: {
                    "description": "Категория не найдена",
                    "content": {"application/json": {}},
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешное получение категории",
                    value={"id": 1, "name": "Category name"},
                    status_codes=["200"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Ошибка: категория не найдена",
                    value={"detail": "No Category matches the given query."},
                    status_codes=["404"],
                    response_only=True,
                ),
            ],
        ),
        update=extend_schema(
            description="Обновить информацию о категории по её ID. Все поля обязательны.",
            summary="Обновление категории",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="Уникальный идентификатор категории (целое число)",
                    required=True,
                ),
            ],
            request=CategorySerializer,
            responses={200: CategorySerializer, **AUTH_ERROR_RESPONSES},
            examples=[
                OpenApiExample(
                    name="Успешное обновление категории",
                    value={"id": 1, "name": "Category name"},
                    status_codes=["200"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Успешное обновление категории",
                    value={"name": "Category name"},
                    status_codes=["200"],
                    request_only=True,
                ),
                *CRUD_ERROR_EXAMPLES,
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        partial_update=extend_schema(
            description="Частичное обновление информации о категории. Поля, которые не переданы в запросе, останутся прежними.",
            summary="Частичное обновление категории.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="Уникальный идентификатор категории (целое число)",
                    required=True,
                ),
            ],
            responses={200: CategorySerializer, **AUTH_ERROR_RESPONSES},
            examples=[
                OpenApiExample(
                    name="Успешное обновление категории",
                    value={"id": 1, "name": "Category new name"},
                    status_codes=["200"],
                    response_only=True,
                ),
                OpenApiExample(
                    name="Успешное обновление категории",
                    value={"name": "Category new name"},
                    status_codes=["200"],
                    request_only=True,
                ),
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
        destroy=extend_schema(
            description="Удалить категорию по ID. Только администратор может удалять категории. Связанные товары будут удалены.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="Уникальный идентификатор категории (целое число)",
                    required=True,
                ),
            ],
            summary="Удалить категорию",
            responses={204: None, **AUTH_ERROR_RESPONSES.pop(400)},
            examples=[
                OpenApiExample(
                    name="Ошибка: категория не найдена",
                    value={"detail": "No Category matches the given query."},
                    status_codes=["404"],
                    response_only=True,
                ),
                *AUTH_ERROR_EXAMPLES,
            ],
        ),
    )
}
