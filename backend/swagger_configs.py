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
    ParameterSerializer,
)

SWAGGER_CONFIGS = {
    "login_schema": extend_schema(
        summary="Авторизация",
        description="Эндпоинт для авторизации пользователя с помощью электронной почты и пароля. Пользователь получает JWT-токены для дальнейшего использования API.",
        request=LoginSerializer,
        responses={
            200: {
                "description": "Успешная авторизация",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Неверные данные запроса",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                description="Пример запроса с корректными данными",
                value={"email": "user@example.com", "password": "string"},
                request_only=True,
            ),
            OpenApiExample(
                name="Успешный ответ",
                description="Пример ответа при успешной авторизации",
                value={
                    "user_id": 1,
                    "email": "user@example.com",
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5c.....",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5c.....",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Не указан пароль",
                description="Пример запроса с пустым паролем",
                value={"email": "user@example.com", "password": ""},
                request_only=True,
            ),
            OpenApiExample(
                name="Не указан пароль",
                description="Пример ответа при пустом поле пароля",
                value={"password": ["This field may not be blank."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Не указана почта",
                description="Пример запроса с пустой почтой",
                value={"email": "", "password": "string"},
                request_only=True,
            ),
            OpenApiExample(
                name="Не указана почта",
                description="Пример ответа при пустой почте",
                value={"email": ["This field may not be blank."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Не указана почта и пароль",
                description="Пример запроса с пустой почтой и пустым паролем",
                value={"email": "", "password": ""},
                request_only=True,
            ),
            OpenApiExample(
                name="Не указана почта и пароль",
                description="Пример ответа при пустой почте и пустом пароле",
                value={
                    "email": ["This field may not be blank."],
                    "password": ["This field may not be blank."],
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Неверный формат почты",
                description="Пример запроса с неверным форматом почты",
                value={"email": "exampleexample.com", "password": "string"},
                request_only=True,
            ),
            OpenApiExample(
                name="Неверный формат почты",
                description="Пример ответа при неверном формате почты",
                value={"email": ["Enter a valid email address."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Неверные данные",
                description="Пример запроса с неверными данными для авторизации",
                value={"email": "user@example.com", "password": "misspelledpassword"},
                request_only=True,
            ),
            OpenApiExample(
                name="Неверные данные",
                description="Пример ответа при неверных данных",
                value={
                    "non_field_errors": [
                        "Не удалось войти с предоставленными учетными данными."
                    ]
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    ),
    "password_reset_schema": extend_schema(
        summary="Сброс пароля",
        description="Эндпоинт для сброса пароля пользователя с помощью отправленного токена. Пользователь получит инструкцию по сбросу пароля.",
        request=PasswordResetSerializer,
        responses={
            200: {
                "description": "Успешный ответ.",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Неверные данные.",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                description="Пример запроса с корректными данными",
                value={"email": "user@example.com"},
                request_only=True,
            ),
            OpenApiExample(
                name="Успешный ответ",
                description="Пример успешного ответа",
                value={"detail": "Ссылка для сброса пароля отправлена на email."},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Неверный формат почты",
                description="Пример запроса с ошибкой в email",
                value={"email": "userexample.com"},
                request_only=True,
            ),
            OpenApiExample(
                name="Неверный формат почты",
                description="Пример ответа при ошибке в email",
                value={"email": ["Enter a valid email address."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Пустая почта",
                description="Пример запроса без email",
                value={"email": ""},
                request_only=True,
            ),
            OpenApiExample(
                name="Пустая почта",
                description="Пример ответа при пустом email",
                value={"email": ["This field may not be blank."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Пользователь не найден",
                description="Пример запроса с незарегистрированным email",
                value={"email": "us@erexample.com"},
                request_only=True,
            ),
            OpenApiExample(
                name="Пользователь не найден",
                description="Пример ответа при отсутствии пользователя",
                value={"email": {"email": ["Пользователь с таким email не найден."]}},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    ),
    "password_reset_confirm_schema": extend_schema(
        summary="Подтверждение нового пароля",
        description="Эндпоинт для установки нового пароля с использованием токена из письма. Требует uid и token из ссылки.",
        parameters=[
            OpenApiParameter(
                name="uidb64",
                description="Base64-кодированный идентификатор пользователя",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="token",
                description="Токен для сброса пароля (временный)",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
        request=PasswordResetConfirmSerializer,
        responses={
            200: {
                "description": "Пароль успешно изменен",
                "content": {
                    "application/json": {
                        "example": {"detail": "Пароль успешно изменен"}
                    }
                },
            },
            400: {
                "description": "Ошибки валидации данных",
                "content": {
                    "application/json": {
                        "examples": {
                            "InvalidToken": {
                                "value": {
                                    "token": ["Недействительный токен сброса пароля"]
                                }
                            },
                            "InvalidUid": {
                                "value": {
                                    "uid": ["Недопустимый идентификатор пользователя"]
                                }
                            },
                            "WeakPassword": {
                                "value": {
                                    "non_field_errors": [
                                        "Пароль должен содержать минимум 8 символов",
                                        "Пароль не может состоять только из цифр",
                                    ]
                                }
                            },
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                description="Пример запроса с валидным паролем",
                value={"new_password": "SecurePass123!"},
                request_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Успешный ответ",
                description="Пример ответа при успешной смене пароля",
                value={"detail": "Пароль успешно изменен"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Неверный токен",
                description="Пример ответа при истечении срока токена",
                value={"token": ["Недействительный токен сброса пароля"]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Неверный идентификатор",
                description="Пример ответа при поврежденной ссылке",
                value={"uid": ["Недопустимый идентификатор пользователя"]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Короткий пароль",
                description="Пример запроса с ненадежным паролем",
                value={"new_password": "123"},
                request_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Ошибка валидации",
                description="Пример ответа для слабого пароля",
                value={
                    "non_field_errors": [
                        "Пароль должен содержать минимум 8 символов",
                        "Пароль должен содержать буквы и цифры",
                    ]
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Пустой пароль",
                description="Пример запроса без пароля",
                value={"new_password": ""},
                request_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Обязательное поле",
                description="Пример ответа при отсутствии пароля",
                value={"new_password": ["Это поле не может быть пустым."]},
                response_only=True,
                status_codes=["400"],
            ),
        ],
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
                    "application/json": {
                        "example": {"message": "Data uploaded successfully."}
                    }
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
        description="Эндпоинт для импорта данных поставщика. Возвращает ID задачи.",
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
                        "example": {"detail": "Вы не связаны с магазином."}
                    }
                },
            },
            401: {
                "description": "Пользователь не авторизован",
                "content": {
                    "application/json": {
                        "example": {"detail": "Пожалуйста, войдите в систему."}
                    }
                },
            },
            500: {
                "description": "Ошибка сервера",
                "content": {
                    "application/json": {
                        "example": {"error": "Ошибка при импорте данных: "}
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
    "check_partner_import_schema": extend_schema(
        summary="Проверка статуса задачи на импорт данных поставщика",
        description="Эндпоинт для проверки статуса задачи импорта. Возвращает текущий статус и результат выполнения.",
        responses={
            200: {
                "description": "Статус задачи",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "SUCCESS",
                            "data": {"message": "Данные успешно импортированы"},
                        }
                    }
                },
            },
            400: {
                "description": "Неверный формат task_id",
                "content": {
                    "application/json": {
                        "example": {"error": "Неверный формат идентификатора задачи"}
                    }
                },
            },
            401: {
                "description": "Пользователь не авторизован",
                "content": {
                    "application/json": {
                        "example": {"detail": "Пожалуйста, войдите в систему."}
                    }
                },
            },
            404: {
                "description": "Задача не найдена",
                "content": {
                    "application/json": {
                        "example": {"error": "Задача с указанным ID не найдена"}
                    }
                },
            },
            500: {
                "description": "Ошибка сервера",
                "content": {
                    "application/json": {
                        "example": {"error": "Внутренняя ошибка сервера"}
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешное выполнение",
                value={
                    "status": "SUCCESS",
                    "data": {"message": "Данные успешно импортированы"},
                },
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Задача в процессе",
                value={"status": "PENDING"},
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Ошибка выполнения",
                value={"status": "FAILURE", "error": "Ошибка валидации данных"},
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Неверный формат ID",
                value={"error": "Неверный формат идентификатора задачи"},
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Задача не найдена",
                value={"error": "Задача с указанным ID не найдена"},
                status_codes=["404"],
            ),
        ],
    ),
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
    ),
    "register_schema": extend_schema(
        summary="Регистрация аккаунта",
        description="Регистрация нового пользователя с подтверждением email",
        request=UserRegistrationSerializer,
        responses={
            201: {
                "description": "Успешная регистрация",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "success",
                            "message": "Регистрация успешна. Проверьте email для активации",
                        }
                    }
                },
            },
            400: {
                "description": "Ошибки валидации",
                "content": {
                    "application/json": {
                        "examples": {
                            "InvalidData": {
                                "value": {
                                    "status": "error",
                                    "errors": {
                                        "email": ["Введите корректный email адрес"],
                                        "password": [
                                            "This password is too short. It must contain at least 8 characters.",
                                            "This password is too common.",
                                            "This password is entirely numeric.",
                                        ],
                                        "role": [
                                            "Неверная роль. Допустимые значения: customer, supplier, admin"
                                        ],
                                    },
                                }
                            },
                            "EmailExists": {
                                "value": {
                                    "status": "error",
                                    "errors": {
                                        "email": [
                                            "Пользователь с таким email уже существует"
                                        ]
                                    },
                                }
                            },
                            "MissingFields": {
                                "value": {
                                    "status": "error",
                                    "errors": {
                                        "email": ["Email обязателен для заполнения"],
                                        "password": ["Пароль не может быть пустым"],
                                        "role": ["Роль обязательна для заполнения"],
                                    },
                                }
                            },
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный запрос",
                value={
                    "email": "user@example.com",
                    "password": "SecurePass123!",
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "role": "customer",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Успешный ответ",
                description="Ответ после успешной регистрации",
                value={
                    "status": "success",
                    "message": "Регистрация успешна. Проверьте email для активации",
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                name="Невалидные данные",
                value={"email": "1", "password": "1", "role": "1"},
                request_only=True,
            ),
            OpenApiExample(
                name="Пример ответа с ошибками",
                value={
                    "status": "error",
                    "errors": {
                        "email": ["Введите корректный email адрес"],
                        "password": [
                            "This password is too short. It must contain at least 8 characters.",
                            "This password is too common.",
                            "This password is entirely numeric.",
                        ],
                        "role": [
                            "Неверная роль. Допустимые значения: customer, supplier, admin"
                        ],
                    },
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Существующий email",
                value={
                    "email": "exists@example.com",
                    "password": "SecurePass123!",
                    "role": "customer",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Ответ для существующего email",
                value={
                    "status": "error",
                    "errors": {"email": ["Пользователь с таким email уже существует"]},
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    ),
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
    ),
    "confirm_registration_schema": extend_schema(
        summary="Активация аккаунта",
        description="Активация аккаунта пользователя с помощью подтверждения по токену, который был отправлен на email.",
        responses={
            200: {
                "description": "Аккаунт успешно активирован",
                "content": {"application/json": {}},
            },
            404: {
                "description": "Пользователь не найден",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Аккаунт успешно активирован",
                value={
                    "Status": "success",
                    "Message": "Ваш аккаунт успешно активирован.",
                },
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Пользователь не найден",
                value={"detail": "No User matches the given query."},
                status_codes=["404"],
            ),
        ],
    ),
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
                "content": {"application/json": {}},
            },
            400: {
                "description": "Ошибка, если пользователь не связан с магазином.",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Список подтвержденных заказов",
                value=[{"id": 1, "status": "confirmed", "items": []}],
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Ошибка, если пользователь не связан с магазином",
                value={"detail": "User is not associated with a shop."},
                status_codes=["400"],
            ),
        ],
    ),
    "user_orders_schema": extend_schema(
        summary="Получить подтвержденные заказы пользователя",
        description="Возвращает список заказов со статусом 'confirmed' для текущего пользователя. Требуется авторизация и права покупателя.",
        responses={
            200: {
                "description": "Список подтвержденных заказов",
                "content": {
                    "application/json": {
                        "examples": {
                            "WithOrders": {
                                "value": [
                                    {
                                        "id": 1,
                                        "user": 1,
                                        "order_items": [
                                            {
                                                "id": 1,
                                                "product": 1,
                                                "shop": 1,
                                                "quantity": 2,
                                            }
                                        ],
                                        "dt": "2025-03-26T21:32:57.257443Z",
                                        "status": "confirmed",
                                    }
                                ]
                            },
                            "EmptyList": {"value": []},
                        }
                    }
                },
            },
            401: {
                "description": "Пользователь не авторизован",
                "content": {
                    "application/json": {
                        "example": {"detail": "Пожалуйста, войдите в систему."}
                    }
                },
            },
            403: {
                "description": "Доступ запрещен",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "У вас недостаточно прав для выполнения этого действия."
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный ответ с заказами",
                description="Пример ответа с существующими заказами",
                value=[
                    {
                        "id": 1,
                        "user": 1,
                        "order_items": [
                            {"id": 1, "product": 1, "shop": 1, "quantity": 2}
                        ],
                        "dt": "2025-03-26T21:32:57.257443Z",
                        "status": "confirmed",
                    }
                ],
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Пустой список",
                description="Пример ответа когда заказов нет",
                value=[],
                response_only=True,
                status_codes=["200"],
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
    "confirm_basket_schema": extend_schema(
        summary="Подтвердить корзину",
        description="Изменяет статус заказа на 'подтвержден' и использует ID контакта для подтверждения.",
        request=OrderWithContactSerializer,
        responses={
            200: {
                "description": "Корзина успешно подтверждена.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Заказ успешно подтвержден."}
                    }
                },
            },
            400: {
                "description": "Ошибка, если корзина пуста или ID контакта некорректен.",
                "content": {
                    "application/json": {"example": {"detail": "Корзина пуста."}}
                },
            },
        },
    ),
    "disable_toggle_user_activity_schema": extend_schema(
        summary="Переключить активность пользователя",
        description="Позволяет администратору включить/отключить активность пользователя. "
        "Требуются права администратора. Нельзя изменять свой аккаунт.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя в системе",
            ),
        ],
        responses={
            200: {
                "description": "Статус активности изменен",
                "content": {
                    "application/json": {
                        "examples": {
                            "Deactivated": {
                                "value": {
                                    "message": "Активность пользователя fleshdota2@yandex.ru (ID=2) изменена на False",
                                    "user_id": 2,
                                    "new_status": False,
                                }
                            },
                            "Activated": {
                                "value": {
                                    "message": "Активность пользователя example@mail.com (ID=3) изменена на True",
                                    "user_id": 3,
                                    "new_status": True,
                                }
                            },
                        }
                    }
                },
            },
            403: {
                "description": "Ошибки доступа",
                "content": {
                    "application/json": {
                        "examples": {
                            "SelfChange": {
                                "value": {
                                    "error": "Вы не можете изменить активность своего аккаунта."
                                }
                            },
                            "NoPermissions": {
                                "value": {
                                    "detail": "У вас недостаточно прав для выполнения этого действия."
                                }
                            },
                        }
                    }
                },
            },
            404: {
                "description": "Пользователь не найден",
                "content": {
                    "application/json": {
                        "example": {"detail": "No User matches the given query."}
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешная деактивация",
                value={
                    "message": "Активность пользователя test@example.com (ID=5) изменена на False",
                    "user_id": 5,
                    "new_status": False,
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Успешная активация",
                value={
                    "message": "Активность пользователя user@mail.org (ID=6) изменена на True",
                    "user_id": 6,
                    "new_status": True,
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Попытка изменить свой аккаунт",
                value={"error": "Вы не можете изменить активность своего аккаунта."},
                response_only=True,
                status_codes=["403"],
            ),
            OpenApiExample(
                name="Недостаточно прав",
                value={
                    "detail": "У вас недостаточно прав для выполнения этого действия."
                },
                response_only=True,
                status_codes=["403"],
            ),
            OpenApiExample(
                name="Пользователь не найден",
                value={"detail": "No User matches the given query."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    ),
    "run_pytest_schema": extend_schema(
        summary="Запуск pytest",
        description="Эндпоинт для запуска pytest. Доступен только для администраторов.",
        responses={
            202: {
                "description": "Задача на выполнение pytest успешно создана.",
                "content": {"application/json": {}},
            },
            403: {
                "description": "Доступ запрещен. Требуются права администратора.",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Задача на выполнение pytest успешно создана",
                value={"task_id": "550e8400-e29b-41d4-a716-446655440000"},
                status_codes=["202"],
            ),
            OpenApiExample(
                name="Доступ запрещен",
                value={"detail": "You do not have permission to perform this action."},
                status_codes=["403"],
            ),
        ],
    ),
    "test_force_sentry_error_schema": extend_schema(
        summary="Запуск принудительной ошибки для Sentry",
        description="Эндпоинт для принудительного запуска ошибки для отправки в Sentry. Доступен только для администраторов.",
        responses={
            500: {
                "description": "Тестовая ошибка успешно сгенерирована и отправлена в Sentry",
                "content": {"application/json": {}},
            },
            401: {
                "description": "Пользователь не авторизован",
                "content": {"application/json": {}},
            },
            403: {
                "description": "Доступ запрещен. Требуются права администратора.",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Тестовая ошибка Sentry",
                value={"error": "Internal server error"},
                status_codes=["500"],
                description="Пример ответа при успешной генерации тестовой ошибки",
            ),
            OpenApiExample(
                name="Пользователь не авторизован",
                value={"detail": "Пожалуйста, войдите в систему."},
                status_codes=["401"],
                description="Пример ответа для неавторизованного пользователя",
            ),
            OpenApiExample(
                name="Доступ запрещен",
                value={
                    "detail": "У вас недостаточно прав для выполнения этого действия."
                },
                status_codes=["403"],
                description="Пример ответа при отсутствии прав администратора",
            ),
        ],
    ),
    "check_pytest_task_schema": extend_schema(
        summary="Проверка статуса задачи pytest",
        description="Эндпоинт для проверки статуса задачи pytest. Возвращает результат выполнения тестов.",
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="ID задачи, возвращенный при запуске pytest.",
            ),
        ],
        responses={
            200: {
                "description": "Результат выполнения тестов.",
                "content": {"application/json": {}},
            },
            202: {
                "description": "Задача ещё выполняется.",
                "content": {"application/json": {}},
            },
            500: {
                "description": "Ошибка при выполнении задачи.",
                "content": {"application/json": {}},
            },
        },
        examples=[
            OpenApiExample(
                name="Результат выполнения тестов",
                value={
                    "status": "SUCCESS",
                    "summary": {
                        "passed": 5,
                        "failed": 1,
                        "errors": 0,
                    },
                    "successful_tests": ["test_example_1", "test_example_2"],
                    "failed_tests": ["test_example_3"],
                },
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Задача ещё выполняется",
                value={"status": "PENDING", "message": "Задача ещё выполняется."},
                status_codes=["202"],
            ),
            OpenApiExample(
                name="Ошибка при выполнении задачи",
                value={"status": "FAILURE", "message": "Задача завершилась с ошибкой."},
                status_codes=["500"],
            ),
        ],
    ),
    "run_coverage_pytest_schema": extend_schema(
        summary="Запуск pytest с измерением покрытия",
        description="Эндпоинт для запуска тестов с измерением покрытия (pytest-cov). "
        "Доступен только для администраторов. Возвращает результаты выполнения тестов и отчет о покрытии.",
        responses={
            200: {
                "description": "Тесты успешно выполнены",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "success",
                            "output": "Результаты выполнения тестов...",
                            "error": "",
                            "coverage": {
                                "total": "81%",
                                "details": {
                                    "backend/models.py": "80%",
                                    "backend/views.py": "83%",
                                },
                            },
                        }
                    }
                },
            },
            400: {
                "description": "Ошибка при выполнении тестов",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "error",
                            "output": "Результаты выполнения тестов...",
                            "error": "Ошибки выполнения тестов...",
                        }
                    }
                },
            },
            403: {
                "description": "Доступ запрещен. Требуются права администратора.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                },
            },
            500: {
                "description": "Внутренняя ошибка сервера",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "error",
                            "message": "Internal server error.",
                        }
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Успешный запуск тестов",
                value={
                    "status": "success",
                    "output": "Результаты выполнения тестов...",
                    "error": "",
                    "coverage": {
                        "total": "81%",
                        "details": {
                            "backend/models.py": "80%",
                            "backend/views.py": "83%",
                        },
                    },
                },
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Ошибка при выполнении тестов",
                value={
                    "status": "error",
                    "output": "Результаты выполнения тестов...",
                    "error": "Ошибки выполнения тестов...",
                },
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Доступ запрещен",
                value={"detail": "You do not have permission to perform this action."},
                status_codes=["403"],
            ),
            OpenApiExample(
                name="Внутренняя ошибка сервера",
                value={"status": "error", "message": "Internal server error."},
                status_codes=["500"],
            ),
        ],
    ),
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
    ),
}
