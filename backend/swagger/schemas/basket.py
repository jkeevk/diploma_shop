# DRF Spectacular
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

# Local imports
from backend.serializers import (
    OrderSerializer,
    OrderItemSerializer,
    OrderWithContactSerializer,
)

common_error_examples = [
    OpenApiExample(
        name="Ошибка авторизации",
        description="Пример ответа для неавторизованного пользователя",
        value={"detail": "Пожалуйста, войдите в систему."},
        response_only=True,
        status_codes=["401"],
    ),
    OpenApiExample(
        name="Ошибка доступа",
        description="Пример ответа при недостатке прав",
        value={"detail": "У вас недостаточно прав для выполнения этого действия."},
        response_only=True,
        status_codes=["403"],
    ),
    OpenApiExample(
        name="Элемент не найден",
        description="Пример ответа при несуществующем элементе или отсутствии прав на элемент.",
        value={"detail": "Корзина не найдена."},
        response_only=True,
        status_codes=["404"],
    ),
]
validation_error_examples = [
    OpenApiExample(
        name="Нет товаров в заказе",
        description="Ошибка при отсутствии order_items",
        value={"order_items": ["Обязательное поле"]},
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Магазин не привязан к пользователю",
        description="Ошибка при неактивном продавце",
        value=["Магазин Books World не привязан к пользователю"],
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Недостаточно товара",
        description="Ошибка при недостаточном количестве товара",
        value=[
            "Недостаточно товара Python Basics (ID=3) в магазине Books World (ID=1). Доступно: 5, запрошено: 10."
        ],
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Некорректный статус",
        description="Попытка установить несуществующий статус. Валидные статусы доступны только для администратора или продавца.",
        value={
            "detail": "Некорректный статус: test. Доступные статусы: new, confirmed, assembled, sent, delivered, canceled"
        },
        response_only=True,
        status_codes=["400"],
    ),
    OpenApiExample(
        name="Недостаточно прав для изменения статуса",
        description="Попытка изменить статус покупателем. Пользователь может создават новый заказ или отменять уже созданный.",
        value={
            "detail": "Недостаточно прав. Вы можете устанавливать только: new, canceled"
        },
        response_only=True,
        status_codes=["400"],
    ),
]

BASKET_SCHEMAS = {
    "basket_viewset_schema": extend_schema_view(
        list=extend_schema(
            summary="Список активных корзин",
            description="Возвращает список активных корзин с заказами пользователя. Требуется авторизация и права покупателя.",
            responses={
                200: {
                    "description": "Список активных корзин пользователя",
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
            },
            examples=[
                OpenApiExample(
                    name="Успешный ответ",
                    description="Пример ответа с активными заказами",
                    value={
                        "id": 1,
                        "user": 1,
                        "order_items": [
                            {"id": 1, "product": 1, "shop": 1, "quantity": 2}
                        ],
                        "dt": "2025-03-26T21:32:57.257443Z",
                        "status": "new",
                    },
                    response_only=True,
                    status_codes=["200"],
                ),
                OpenApiExample(
                    name="Пустая корзина",
                    description="Пример ответа когда нет позиций в корзине",
                    value=[],
                    response_only=True,
                    status_codes=["200"],
                ),
                common_error_examples[0],
                common_error_examples[1],
            ],
        ),
        create=extend_schema(
            summary="Создать новую корзину",
            description="Создает новую корзину для пользователя. Требуется авторизация и права покупателя.",
            request=OrderSerializer,
            responses={
                201: {
                    "description": "Корзина успешно создана",
                    "content": {"application/json": {}},
                },
                400: {
                    "description": "Ошибки валидации: отсутствие товаров, неактивный продавец, недостаток товара",
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
                404: {
                    "description": "Элемент не найден",
                    "content": {"application/json": {}},
                },
            },
            examples=[
                OpenApiExample(
                    name="Успешный запрос",
                    description="Пример запроса на создание корзины с валидными данными",
                    value={
                        "user": 1,
                        "order_items": [{"product": 3, "shop": 1, "quantity": 5}],
                    },
                    request_only=True,
                    status_codes=["201"],
                ),
                OpenApiExample(
                    name="Корзина успешно создана",
                    description="Пример ответа после успешного создания корзины",
                    value={
                        "id": 7,
                        "user": 1,
                        "order_items": [
                            {"id": 46, "product": 1, "shop": 1, "quantity": 1}
                        ],
                        "dt": "2025-03-27T16:22:18.768645Z",
                        "status": "new",
                    },
                    response_only=True,
                    status_codes=["201"],
                ),
                OpenApiExample(
                    name="Недостаточно товара",
                    description="Пример запроса на создание корзины с количеством товара превышающим количество товара в магазине",
                    value={
                        "id": 1,
                        "user": 1,
                        "order_items": [{"product": 3, "shop": 1, "quantity": 999}],
                    },
                    request_only=True,
                    status_codes=["400"],
                ),
                OpenApiExample(
                    name="Комбинированная ошибка",
                    description="Пример запроса на создание корзины с несуществующими данными",
                    value={
                        "id": 999,
                        "user": 999,
                        "order_items": [{"product": 999, "shop": 999, "quantity": 999}],
                    },
                    request_only=True,
                    status_codes=["400"],
                ),
                OpenApiExample(
                    name="Комбинированная ошибка",
                    description="Пример ответа на создание корзины с несуществующими данными",
                    value={
                        "user": ["Пользователь с ID=999 не существует"],
                        "order_items": [
                            {
                                "product": ["Товар с ID=999 не существует"],
                                "shop": ["Магазин с ID=999 не существует"],
                            }
                        ],
                    },
                    response_only=True,
                    status_codes=["400"],
                ),
                *validation_error_examples,
                *common_error_examples,
            ],
        ),
        retrieve=extend_schema(
            summary="Получить корзину по ID",
            description="Возвращает корзину по указанному ID. Требуется авторизация и права покупателя.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                200: {
                    "description": "Корзина найдена",
                    "content": {"application/json": {}},
                },
                404: {
                    "description": "Корзина не найдена",
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
            },
            examples=[
                OpenApiExample(
                    name="Корзина найдена",
                    description="Пример ответа с найденной корзиной",
                    value={
                        "id": 1,
                        "user": 1,
                        "order_items": [
                            {"id": 1, "product": 1, "shop": 1, "quantity": 2}
                        ],
                        "dt": "2025-03-26T21:32:57.257443Z",
                        "status": "new",
                    },
                    response_only=True,
                    status_codes=["200"],
                ),
                OpenApiExample(
                    name="Корзина не найдена",
                    description="Пример ответа, когда корзина не найдена",
                    value={"detail": "Корзина не найдена."},
                    response_only=True,
                    status_codes=["404"],
                ),
                *common_error_examples,
            ],
        ),
        update=extend_schema(
            summary="Обновить корзину по ID",
            description="Обновляет корзину по указанному ID. Требуется авторизация. Пользователи могут менять статусы new/canceled, админы и продавцы - любые.",
            request=OrderSerializer,
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                200: {
                    "description": "Корзина успешно обновлена",
                    "content": {"application/json": {}},
                },
                400: {
                    "description": "Ошибки: неверный статус, недостаток прав, проблемы с товарами",
                    "content": {"application/json": {}},
                },
                404: {
                    "description": "Корзина не найдена",
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
            },
            examples=[
                OpenApiExample(
                    name="Корзина успешно обновлена",
                    description="Пример ответа после полного обновления",
                    value={
                        "id": 1,
                        "user": 1,
                        "order_items": [
                            {"id": 1, "product": 1, "shop": 1, "quantity": 3}
                        ],
                        "dt": "2025-03-26T21:32:57.257443Z",
                        "status": "new",
                    },
                    response_only=True,
                    status_codes=["200"],
                ),
                OpenApiExample(
                    name="Элемент не найден",
                    description="Ошибка при обновлении несуществующего элемента",
                    value={"detail": "Элемент заказа не найден для обновления"},
                    response_only=True,
                    status_codes=["400"],
                ),
                OpenApiExample(
                    name="Недостаточно прав",
                    description="Ошибка при обновлении корзины с недостаточными правами",
                    value={"detail": "Недостаточно прав"},
                    response_only=True,
                    status_codes=["403"],
                ),
                *validation_error_examples,
                *common_error_examples,
            ],
        ),
        partial_update=extend_schema(
            summary="Частичное обновление корзины",
            description="Частично обновляет корзину. Требуется авторизация. Пользователи могут менять статусы new/canceled, админы и продавцы - любые. Все пользователи могут менять статус и количество товаров.",
            request=OrderSerializer,
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                200: {
                    "description": "Корзина успешно обновлена",
                    "content": {"application/json": {}},
                },
                400: {
                    "description": "Ошибки: неверный статус, недостаток прав, проблемы с товарами",
                    "content": {"application/json": {}},
                },
                404: {
                    "description": "Корзина не найдена",
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
            },
            examples=[
                OpenApiExample(
                    name="Успешное частичное обновление",
                    description="Пример изменения количества товара",
                    value={"order_items": [{"product": 1, "quantity": 2}]},
                    request_only=True,
                    status_codes=["200"],
                ),
                OpenApiExample(
                    name="Успешный ответ",
                    description="Ответ после частичного обновления",
                    value={
                        "id": 1,
                        "user": 1,
                        "order_items": [
                            {"id": 1, "product": 1, "shop": 1, "quantity": 2}
                        ],
                        "dt": "2025-03-26T21:32:57.257443Z",
                        "status": "new",
                    },
                    response_only=True,
                    status_codes=["200"],
                ),
                OpenApiExample(
                    name="Отмена заказа",
                    description="Пример запроса для отмены заказа (изменяет статус на canceled)",
                    value={
                        "order_items": [{"product": 1, "quantity": 2}],
                        "status": "canceled",
                    },
                    request_only=True,
                    status_codes=["200"],
                ),
                OpenApiExample(
                    name="Ошибка доступа к статусу",
                    description="Покупатель пытается изменить статус",
                    value=[
                        "Недостаточно прав. Вы можете устанавливать только: new, canceled"
                    ],
                    response_only=True,
                    status_codes=["400"],
                ),
                *validation_error_examples,
                *common_error_examples,
            ],
        ),
        destroy=extend_schema(
            summary="Удалить корзину по ID",
            description="Удаляет корзину по указанному ID. Требуется авторизация и права покупателя для удаление своей корзины. Админы и продавцы могут удалять любые корзины.",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    description="ID корзины в системе",
                ),
            ],
            responses={
                204: {
                    "description": "Корзина успешно удалена",
                    "content": {"application/json": {}},
                },
                404: {
                    "description": "Корзина не найдена",
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
            },
            examples=[
                OpenApiExample(
                    name="Корзина успешно удалена",
                    description="Пример ответа после удаления корзины",
                    value=[],
                    response_only=True,
                    status_codes=["204"],
                ),
                OpenApiExample(
                    name="Корзина не найдена",
                    description="Пример ответа, когда корзина не найдена",
                    value={"detail": "Корзина не найдена."},
                    response_only=True,
                    status_codes=["404"],
                ),
                *common_error_examples,
            ],
        ),
    ),
    "confirm_basket_schema": extend_schema(
        summary="Подтвердить корзину",
        description="Подтвердить заказ. Изменяет статус корзины на 'подтвержден' и использует ID контакта (адрес доставки) для подтверждения.",
        request=OrderWithContactSerializer,
        responses={
            200: {
                "description": "Корзина успешно подтверждена.",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Ошибка валидации: пустая корзина, неверный ID контакта или отсутствие контакта",
                "content": {"application/json": {}},
            },
            401: {
                "description": "Пользователь не авторизован.",
                "content": {"application/json": {}},
            },
            403: {
                "description": "Доступ запрещен (недостаточно прав).",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Успешное подтверждение",
                description="Пример успешного подтверждения корзины",
                value={"detail": "Заказ успешно подтвержден."},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Пустая корзина",
                description="Пример ошибки при пустой корзине",
                value={"non_field_errors": ["Корзина пуста."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Отсутствует contact_id",
                description="Пример ошибки при отсутствии ID контакта",
                value={"contact_id": ["ID контакта обязателен."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Неверный contact_id",
                description="Пример ошибки при несуществующем ID контакта",
                value={"contact_id": ["Неверный ID контакта."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Чужой contact_id",
                description="Пример ошибки при использовании контакта другого пользователя",
                value={"contact_id": ["Контакт не найден."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Ошибка авторизации",
                description="Пример ответа для неавторизованного пользователя",
                value={"detail": "Пожалуйста, войдите в систему."},
                response_only=True,
                status_codes=["401"],
            ),
            OpenApiExample(
                name="Ошибка доступа",
                description="Пример ответа при недостатке прав",
                value={
                    "detail": "У вас недостаточно прав для выполнения этого действия."
                },
                response_only=True,
                status_codes=["403"],
            ),
        ],
    ),
}
