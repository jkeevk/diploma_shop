from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from backend.serializers import ParameterSerializer


PARAMETER_SCHEMAS = {
    "parameter_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех параметров.",
            summary="Список параметров",
            responses={200: ParameterSerializer(many=True)},
        ),
        create=extend_schema(
            description="Создать новый параметр.",
            summary="Создание параметра",
            request=ParameterSerializer,
            responses={201: ParameterSerializer},
        ),
        retrieve=extend_schema(
            description="Получить параметр по ID.",
            summary="Получение параметра",
            responses={200: ParameterSerializer},
        ),
        update=extend_schema(
            description="Обновить параметр по ID.",
            summary="Обновление параметра",
            request=ParameterSerializer,
            responses={200: ParameterSerializer},
        ),
        partial_update=extend_schema(
            description="Частичное обновление параметра по ID.",
            summary="Частичное обновление параметра",
            request=ParameterSerializer,
            responses={200: ParameterSerializer},
        ),
        destroy=extend_schema(
            description="Удалить параметр по ID.",
            summary="Удаление параметра",
            responses={204: None},
        ),
    )
}
