from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from backend.serializers import ContactSerializer


CONTACT_SCHEMAS = {
    "contact_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех контактов компании.",
            summary="Список контактов",
            responses={200: ContactSerializer(many=True)},
        ),
        create=extend_schema(
            description="Создать новый контакт для компании.",
            summary="Создание контакта",
            request=ContactSerializer,
            responses={201: ContactSerializer},
        ),
        retrieve=extend_schema(
            description="Получить контакт по ID.",
            summary="Получение контакта",
            responses={200: ContactSerializer},
        ),
        update=extend_schema(
            description="Обновить контакт по ID.",
            summary="Обновление контакта",
            request=ContactSerializer,
            responses={200: ContactSerializer},
        ),
        partial_update=extend_schema(
            description="Частичное обновление контакта по ID.",
            summary="Частичное обновление контакта",
            request=ContactSerializer,
            responses={200: ContactSerializer},
        ),
        destroy=extend_schema(
            description="Удалить контакт по ID.",
            summary="Удаление контакта",
            responses={204: None},
        ),
    )
}
