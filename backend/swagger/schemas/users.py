from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import UserSerializer

USERS_SCHEMAS = {
    "user_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех пользователей.",
            summary="Список пользователей",
            responses={200: UserSerializer(many=True)},
        ),
        create=extend_schema(
            description="Создать нового пользователя.",
            summary="Создание пользователя",
            request=UserSerializer,
            responses={201: UserSerializer},
        ),
        retrieve=extend_schema(
            description="Получить пользователя по ID.",
            summary="Получение пользователя",
            responses={200: UserSerializer},
        ),
        update=extend_schema(
            description="Обновить информацию о пользователе по ID.",
            summary="Обновление пользователя",
            request=UserSerializer,
            responses={200: UserSerializer},
        ),
        partial_update=extend_schema(
            description="Частичное обновление информации о пользователе.",
            summary="Частичное обновление пользователя",
            request=UserSerializer,
            responses={200: UserSerializer},
        ),
        destroy=extend_schema(
            description="Удалить пользователя по ID.",
            summary="Удаление пользователя",
            responses={204: None},
        ),
    )
}
