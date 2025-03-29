from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import ProductSerializer

PRODUCT_SCHEMAS = {
    "product_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех товаров. Фильтрация возможна по категории, имени товара и модели.",
            summary="Список товаров",
            responses={200: ProductSerializer(many=True)},
        ),
        create=extend_schema(
            description="Создать новый товар в каталоге.",
            summary="Создание товара",
            request=ProductSerializer,
            responses={201: ProductSerializer},
        ),
        retrieve=extend_schema(
            description="Получить информацию о товаре по его ID.",
            summary="Получение товара",
            responses={200: ProductSerializer},
        ),
        update=extend_schema(
            description="Обновить информацию о товаре по его ID.",
            summary="Обновление товара",
            request=ProductSerializer,
            responses={200: ProductSerializer},
        ),
        partial_update=extend_schema(
            description="Частичное обновление информации о товаре.",
            summary="Частичное обновление товара",
            request=ProductSerializer,
            responses={200: ProductSerializer},
        ),
        destroy=extend_schema(
            description="Удалить товар из каталога по ID.",
            summary="Удаление товара",
            responses={204: None},
        ),
    )
}
