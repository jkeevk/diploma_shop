from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
    
)
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    LoginSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    ProductSerializer,
    UserRegistrationSerializer,
    ContactSerializer,
    UserSerializer,
    OrderSerializer,
    CategorySerializer,
    ShopSerializer,
    OrderItemSerializer,
    OrderWithContactSerializer
)

SWAGGER_CONFIGS = {
    "login_schema": extend_schema(
        summary="Авторизация",
        description="Эндпоинт для авторизации пользователя с помощью электронной почты и пароля. Пользователь получает доступ к API, используя токен.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Успешная авторизация",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value={
                            "user_id": 1,
                            "email": "user@example.com",
                            "access_token": "string",
                            "refresh_token": "string",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Неверные данные запроса",
                examples=[
                    OpenApiExample(
                        "Пример ошибки авторизации",
                        value={"non_field_errors": ["Invalid credentials."]},
                    )
                ],
            ),
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
    ),
    "password_reset_schema": extend_schema(
        summary="Сброс пароля",
        description="Эндпоинт для сброса пароля пользователя с помощью отправленного токена. Пользователь получит инструкцию по сбросу пароля.",
        request=PasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                description="Ссылка для сброса пароля отправлена на email."
            ),
            400: OpenApiResponse(description="Неверный или отсутствующий токен"),
            404: OpenApiResponse(description="Пользователь не найден"),
        },
    ),
    "password_reset_confirm_schema": extend_schema(
        summary="Подтверждение нового пароля",
        description="Эндпоинт для создания нового пароля с помощью предоставленного токена и uid пользователя.",
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Пароль успешно изменён."),
            400: OpenApiResponse(
                description="Недействительный токен или пользователь не найден."
            ),
            404: OpenApiResponse(description="Пользователь не найден"),
        },
    ),
    "partner_update_schema": extend_schema(
        summary="Обновление каталога поставщика",
        description="Эндпоинт для обновления каталога поставщика. Требует multipart/form-data в теле запроса. Файл должен быть в формате JSON. Используется для загрузки данных о товарах.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                    }
                },
            }
        },
        responses={
            200: OpenApiResponse(description="Данные успешно загружены"),
            400: OpenApiResponse(
                description="Неверный запрос (неверный файл или файл не загружен)"
            ),
            500: OpenApiResponse(description="Внутренняя ошибка сервера"),
        },
    ),
    "product_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список товаров. Фильтрация возможна по категории, имени товара и модели.",
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
    ),
    "register_schema": extend_schema(
        summary="Регистрация аккаунта",
        description="Регистрация нового пользователя с помощью электронной почты и пароля. Включает в себя подтверждение email для активации аккаунта.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                description="Пользователь успешно зарегистрирован и email подтверждён",
            ),
            400: OpenApiResponse(
                description="Пользователь с таким email уже существует",
            ),
        },
    ),
    "confirm_registration_schema": extend_schema(
        summary="Активация аккаунта",
        description="Активация аккаунта пользователя с помощью подтверждения по токену, который был отправлен на email.",
        responses={
            200: OpenApiResponse(description="Аккаунт успешно активирован"),
            404: OpenApiResponse(
                description="Пользователь не найден или неверный токен"
            ),
        },
    ),
    "category_schema": extend_schema(
        summary="Список всех категорий",
        description="Возвращает список всех доступных категорий товаров в магазине.",
        responses={200: CategorySerializer(many=True)},
    ),
    "shop_schema": extend_schema(
        summary="Список всех магазинов",
        description="Возвращает список всех магазинов в системе.",
        responses={200: ShopSerializer(many=True)},
    ),
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
    ),
    "user_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех пользователей системы.",
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
    ),
    "order_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить список всех заказов пользователя.",
            summary="Список заказов",
            responses={200: OrderSerializer(many=True)},
        ),
        create=extend_schema(
            description="Создать новый заказ.",
            summary="Создание заказа",
            request=OrderSerializer,
            responses={201: OrderSerializer},
        ),
        retrieve=extend_schema(
            description="Получить заказ по ID.",
            summary="Получение заказа",
            responses={200: OrderSerializer},
        ),
        update=extend_schema(
            description="Обновить информацию о заказе по ID.",
            summary="Обновление заказа",
            request=OrderSerializer,
            responses={200: OrderSerializer},
        ),
        partial_update=extend_schema(
            description="Частичное обновление заказа по ID.",
            summary="Частичное обновление заказа",
            request=OrderSerializer,
            responses={200: OrderSerializer},
        ),
        destroy=extend_schema(
            description="Удалить заказ по ID.",
            summary="Удаление заказа",
            responses={204: None},
        ),
    ),
    "basket_viewset_schema": extend_schema_view(
        list=extend_schema(
            description="Получить активную корзину пользователя.",
            summary="Список активных корзин пользователя",
            responses={200: OrderSerializer(many=True)},
        ),
        create=extend_schema(
            description="Создать новую корзину для пользователя.",
            summary="Создание корзины",
            request=OrderSerializer,
            responses={201: OrderSerializer},
        ),
        retrieve=extend_schema(
            description="Получить корзину по ID.",
            summary="Получение корзины",
            responses={200: OrderSerializer},
        ),
        update=extend_schema(
            description="Обновить корзину по ID.",
            summary="Обновление корзины",
            request=OrderSerializer,
            responses={200: OrderSerializer},
        ),
        partial_update=extend_schema(
            description="Частичное обновление корзины по ID.",
            summary="Частичное обновление корзины",
            request=OrderSerializer,
            responses={200: OrderSerializer},
        ),
        destroy=extend_schema(
            description="Удалить корзину по ID.",
            summary="Удаление корзины",
            responses={204: None},
        ),
        add_item=extend_schema(
            description="Добавить товар в корзину.",
            summary="Добавление товара в корзину",
            request=OrderItemSerializer,
            responses={200: OrderItemSerializer},
        ),
        remove_item=extend_schema(
            description="Удалить товар из корзины.",
            summary="Удаление товара из корзины",
            request=OrderItemSerializer,
            responses={204: None},
        ),
        update_item_quantity=extend_schema(
            description="Обновить количество товара в корзине.",
            summary="Обновление количества товара в корзине",
            request=OrderItemSerializer,
            responses={200: OrderItemSerializer},
        ),
        total_cost=extend_schema(
            description="Получить общую стоимость корзины.",
            summary="Получение общей стоимости корзины",
            responses={
                200: {
                    "type": "object",
                    "properties": {"total_cost": {"type": "number"}},
                }
            },
        ),
    ),
    "partner_orders_schema": extend_schema(
        summary="Получить подтвержденные заказы для партнера",
        description="Возвращает список подтвержденных заказов для магазина, связанного с текущим пользователем.",
        responses={
            200: OrderSerializer(many=True),
            400: OpenApiResponse(description="Ошибка, если пользователь не связан с магазином.")
        }
    ),
    "confirm_basket_schema": extend_schema(
        summary="Подтвердить корзину",
        description="Изменяет статус заказа на 'подтвержден' и использует ID контакта для подтверждения.",
        request=OrderWithContactSerializer,
        responses={
            200: OrderWithContactSerializer,
            400: OpenApiResponse(description="Ошибка, если корзина пуста или ID контакта некорректен.")
        }
    )
}
