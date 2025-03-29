from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from backend.serializers import CategorySerializer


CATEGORY_SCHEMAS = {
    "category_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех категорий. Фильтрация возможна по названию.",
            summary="Список категорий",
            responses={200: CategorySerializer(many=True)},
        ),
        create=extend_schema(
            description="Создать новую категорию.",
            summary="Создание категории",
            request=CategorySerializer,
            responses={201: CategorySerializer},
        ),
        retrieve=extend_schema(
            description="Получить информацию о категории по её ID.",
            summary="Получение категории",
            responses={200: CategorySerializer},
        ),
        update=extend_schema(
            description="Обновить информацию о категории по её ID.",
            summary="Обновление категории",
            request=CategorySerializer,
            responses={200: CategorySerializer},
        ),
        partial_update=extend_schema(
            description="Частичное обновление информации о категории.",
            summary="Частичное обновление категории",
            request=CategorySerializer,
            responses={200: CategorySerializer},
        ),
        destroy=extend_schema(
            description="Удалить категорию по ID.",
            summary="Удаление категории",
            responses={204: None},
        ),
    )
}
