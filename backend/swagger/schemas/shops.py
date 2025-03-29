from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from backend.serializers import ShopSerializer

SHOP_SCHEMAS = {
    "shop_schema": extend_schema_view(
        get=extend_schema(
            description="Получить список всех магазинов.",
            summary="Список магазинов",
            responses={
                200: ShopSerializer(many=True),
                401: "Необходима аутентификация",
            },
        ),
        post=extend_schema(
            description="Создать новый магазин и связать его с текущим пользователем. Только пользователи с ролью admin или supplier могут выполнять этот запрос.",
            summary="Создание магазина",
            request=ShopSerializer,
            responses={
                201: ShopSerializer,
                403: "У вас недостаточно прав для выполнения этого действия.",
                400: "Некорректные данные запроса.",
            },
        ),
    )
}
