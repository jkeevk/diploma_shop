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
from .serializers import (
    CategorySerializer,
    ContactSerializer,
    LoginSerializer,
    OrderItemSerializer,
    OrderSerializer,
    OrderWithContactSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    ProductSerializer,
    ShopSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

SWAGGER_CONFIGS = {
    "login_schema": extend_schema(
        summary="Авторизация",
        description="Эндпоинт для авторизации пользователя с помощью электронной почты и пароля. Пользователь получает доступ к API, используя токен.",
        request=LoginSerializer,
        responses={
            200: {
                "description": "Успешная авторизация",
                "content": {
                    "application/json": {
                        "example": {
                            "user_id": 1,
                            "email": "user@example.com",
                            "access_token": "string",
                            "refresh_token": "string",
                        }
                    }
                },
            },
            400: {
                "description": "Неверные данные запроса",
                "content": {
                    "application/json": {
                        "example": {"non_field_errors": ["Invalid credentials."]}
                    }
                },
            },
            401: {
                "description": "Неавторизованный доступ",
                "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
            },
        },
    ),
    "password_reset_schema": extend_schema(
        summary="Сброс пароля",
        description="Эндпоинт для сброса пароля пользователя с помощью отправленного токена. Пользователь получит инструкцию по сбросу пароля.",
        request=PasswordResetSerializer,
        responses={
            200: {
                "description": "Ссылка для сброса пароля отправлена на email.",
                "content": {
                    "application/json": {
                        "example": {"message": "Password reset link sent to email."}
                    }
                },
            },
            400: {
                "description": "Неверный или отсутствующий токен",
                "content": {
                    "application/json": {
                        "example": {"detail": "Invalid or missing token."}
                    }
                },
            },
            404: {
                "description": "Пользователь не найден",
                "content": {
                    "application/json": {"example": {"detail": "User not found."}}
                },
            },
        },
    ),
    "password_reset_confirm_schema": extend_schema(
        summary="Подтверждение нового пароля",
        description="Эндпоинт для создания нового пароля с помощью предоставленного токена и uid пользователя.",
        request=PasswordResetConfirmSerializer,
        responses={
            200: {
                "description": "Пароль успешно изменён.",
                "content": {
                    "application/json": {"example": {"message": "Password reset successful."}}
                },
            },
            400: {
                "description": "Недействительный токен или пользователь не найден.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Invalid token or user not found."}
                    }
                },
            },
            404: {
                "description": "Пользователь не найден",
                "content": {
                    "application/json": {"example": {"detail": "User not found."}}
                },
            },
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
            200: {
                "description": "Данные успешно загружены",
                "content": {
                    "application/json": {"example": {"message": "Data uploaded successfully."}}
                },
            },
            400: {
                "description": "Неверный запрос (неверный файл или файл не загружен)",
                "content": {
                    "application/json": {
                        "example": {"detail": "Invalid file or file not uploaded."}
                    }
                },
            },
            500: {
                "description": "Внутренняя ошибка сервера",
                "content": {
                    "application/json": {"example": {"error": "Internal server error."}}
                },
            },
        },
    ),
    "partner_import_schema": extend_schema(
        summary="Импорт данных поставщика",
        description="Эндпоинт для импорта данных поставщика. Возвращает JSON-файл с данными о товарах, категориях и магазине. Доступен только для авторизованных пользователей, связанных с магазином.",
        responses={
            200: {
                "description": "Задача на импорт данных поставлена в очередь",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Задача на импорт данных поставлена в очередь"
                        }
                    }
                },
            },
            400: {
                "description": "Пользователь не связан с магазином",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Вы не связаны с магазином."
                        }
                    }
                },
            },
            401: {
                "description": "Пользователь не авторизован",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Пожалуйста, войдите в систему."
                        }
                    }
                },
            },
            500: {
                "description": "Ошибка сервера",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Ошибка при импорте данных: "
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                value={"message": "Задача на импорт данных поставлена в очередь"},
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Ошибка: пользователь не связан с магазином",
                value={"detail": "Вы не связаны с магазином."},
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Ошибка: пользователь не авторизован",
                value={"detail": "Пожалуйста, войдите в систему."},
                status_codes=["401"],
            ),
            OpenApiExample(
                name="Ошибка сервера",
                value={"error": "Ошибка при импорте данных: "},
                status_codes=["500"],
            ),
        ],
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
            201: {
                "description": "Пользователь успешно зарегистрирован и email подтверждён",
                "content": {
                    "application/json": {
                        "example": {"message": "User registered successfully."}
                    }
                },
            },
            400: {
                "description": "Пользователь с таким email уже существует",
                "content": {
                    "application/json": {
                        "example": {"detail": "User with this email already exists."}
                    }
                },
            },
        },
    ),
    "confirm_registration_schema": extend_schema(
        summary="Активация аккаунта",
        description="Активация аккаунта пользователя с помощью подтверждения по токену, который был отправлен на email.",
        responses={
            200: {
                "description": "Аккаунт успешно активирован",
                "content": {
                    "application/json": {"example": {"message": "Account activated successfully."}}
                },
            },
            404: {
                "description": "Пользователь не найден или неверный токен",
                "content": {
                    "application/json": {"example": {"detail": "User not found or invalid token."}}
                },
            },
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
    ),
    "partner_orders_schema": extend_schema(
        summary="Получить подтвержденные заказы для партнера",
        description="Возвращает список подтвержденных заказов для магазина, связанного с текущим пользователем.",
        responses={
            200: {
                "description": "Список подтвержденных заказов",
                "content": {
                    "application/json": {
                        "example": [{"id": 1, "status": "confirmed", "items": []}]
                    }
                },
            },
            400: {
                "description": "Ошибка, если пользователь не связан с магазином.",
                "content": {
                    "application/json": {
                        "example": {"detail": "User is not associated with a shop."}
                    }
                },
            },
        },
    ),
    "confirm_basket_schema": extend_schema(
        summary="Подтвердить корзину",
        description="Изменяет статус заказа на 'подтвержден' и использует ID контакта для подтверждения.",
        request=OrderWithContactSerializer,
        responses={
            200: {
                "description": "Корзина успешно подтверждена",
                "content": {
                    "application/json": {
                        "example": {"message": "Basket confirmed successfully."}
                    }
                },
            },
            400: {
                "description": "Ошибка, если корзина пуста или ID контакта некорректен.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Basket is empty or invalid contact ID."}
                    }
                },
            },
        },
    ),
}
