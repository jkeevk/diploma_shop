from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from backend.serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)

AUTH_ERROR_EXAMPLES = [
    OpenApiExample(
        name="Ошибка: пользователь не авторизован",
        value={"detail": "Пожалуйста, войдите в систему."},
        status_codes=["401"],
        response_only=True,
    ),
    OpenApiExample(
        name="Ошибка: доступ запрещен",
        value={"detail": "У вас недостаточно прав для выполнения этого действия."},
        status_codes=["403"],
        response_only=True,
    ),
]

USER_ERROR_RESPONSES = {
    400: {"description": "Некорректные данные", "content": {"application/json": {}}},
    401: {"description": "Не авторизован", "content": {"application/json": {}}},
    403: {"description": "Доступ запрещен", "content": {"application/json": {}}},
}

USER_SCHEMAS = {
    "disable_toggle_user_activity_schema": extend_schema(
        summary="Переключить активность пользователя",
        description="Позволяет администратору активировать или деактивировать учетную запись пользователя. При отключенной активности владельца пользователю будет недоступна возможность совершать заказы в магазине."
        "Требуются права администратора. Нельзя изменять свой аккаунт.",
        tags=["Администрирование"],
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
                "description": "Успешная авторизация",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Неверные данные запроса",
                "content": {"application/json": {}},
            },
            403: {
                "description": "Доступ запрещен",
                "content": {"application/json": {}},
            },
            404: {
                "description": "Пользователь не найден",
                "content": {"application/json": {}},
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
    "login_schema": extend_schema(
        summary="Авторизация",
        description="Эндпоинт для авторизации пользователя с помощью электронной почты и пароля. Пользователь получает JWT-токены для дальнейшего использования API.",
        request=LoginSerializer,
        tags=["Авторизация"],
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
        tags=["Пользователь"],
        responses={
            200: {
                "description": "Успешный запрос",
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
        tags=["Пользователь"],
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
    "user_orders_schema": extend_schema(
        summary="Получить подтвержденные заказы",
        description="Возвращает список заказов со статусом 'confirmed' для текущего пользователя. Требуется авторизация и права покупателя.",
        tags=["Пользователь"],
        responses={
            200: {
                "description": "Успешный ответ.",
                "content": {"application/json": {}},
            },
            400: {
                "description": "Неверные данные.",
                "content": {"application/json": {}},
            },
            401: {
                "description": "Пользователь не авторизован.",
                "content": {"application/json": {}},
            },
            403: {
                "description": "Доступ запрещен.",
                "content": {"application/json": {}},
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
    "register_schema": extend_schema(
        summary="Регистрация аккаунта",
        description="Регистрация нового пользователя с подтверждением email",
        tags=["Регистрация"],
        request=UserRegistrationSerializer,
        responses={
            201: {
                "description": "Успешная регистрация.",
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
    "confirm_registration_schema": extend_schema(
        summary="Активация аккаунта",
        description="Активация аккаунта пользователя с помощью подтверждения по токену, который был отправлен на email.",
        tags=["Регистрация"],
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
    "google_auth_schema": extend_schema(
        summary="Страница авторизации через Google",
        description="Этот эндпоинт рендерит HTML-страницу для авторизации через Google. Для начала авторизации перейдите по следующей ссылке: [https://localhost/api/social/google/login](https://localhost/api/social/google/login).",
        responses={
            200: {
                "description": "Страница для авторизации через Google",
                "content": {
                    "text/html": {
                        "example": "<html><body>Login page content here</body></html>"
                    }
                },
            }
        },
        tags=["Авторизация"],
        operation_id="render_google_login",
    ),
    "vk_auth_schema": extend_schema(
        summary="Страница авторизации через VK",
        description="Этот эндпоинт рендерит HTML-страницу для авторизации через VK. Для начала авторизации перейдите по следующей ссылке: [https://localhost/api/social/vk/login](https://localhost/api/social/vk/login).",
        responses={
            200: {
                "description": "Страница для авторизации через VK",
                "content": {
                    "text/html": {
                        "example": "<html><body>Login page content here</body></html>"
                    }
                },
            }
        },
        tags=["Авторизация"],
        operation_id="render_vk_login",
    ),
    "user_upload_image": extend_schema(
        summary="Обновление аватара",
        description="""## Загрузка/обновление аватара пользователя
        * Поддерживаемые форматы: JPEG, PNG
        * Максимальный размер файла: 5MB
        * При повторной загрузке старое изображение заменяется
        * Миниатюра генерируется автоматически""",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "avatar": {
                        "type": "string",
                        "format": "binary",
                        "description": "Файл изображения (обязательное поле)",
                    }
                },
                "required": ["avatar"],
            }
        },
        responses={
            200: {"description": "Изображение загружено"},
            **USER_ERROR_RESPONSES,
        },
        tags=["Пользователь"],
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={"avatar": "файл.jpg"},
                request_only=True,
                media_type="multipart/form-data",
            ),
            OpenApiExample(
                name="Успешная загрузка изображения",
                value={
                    "id": 1,
                    "email": "admin@admin.com",
                    "first_name": "Admin",
                    "last_name": "Admin",
                    "role": "admin",
                    "avatar_thumbnail": "/media/CACHE/images/avatars/Boki-avatar/d3fdf2e63113bf2dfc19d8a92745f433.jpg",
                },
                status_codes=["200"],
                response_only=True,
            ),
            OpenApiExample(
                name="Недопустимый формат файла",
                value={
                    "image": [
                        "File extension “txt” is not allowed. Allowed extensions are: bmp, dib, gif, jfif, jpe, jpg, jpeg, pbm, pgm, ppm, pnm, pfm, png, apng, blp, bufr, cur, pcx, dcx, dds, ps, eps, fit, fits, fli, flc, ftc, ftu, gbr, grib, h5, hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, ico, im, iim, mpg, mpeg, tif, tiff, mpo, msp, palm, pcd, pdf, pxr, psd, qoi, bw, rgb, rgba, sgi, ras, tga, icb, vda, vst, webp, wmf, emf, xbm, xpm."
                    ]
                },
                status_codes=["400"],
                response_only=True,
            ),
            OpenApiExample(
                name="Невалидный файл",
                value={
                    "image": [
                        "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
                    ]
                },
                status_codes=["400"],
                response_only=True,
            ),
            *AUTH_ERROR_EXAMPLES,
        ],
    ),
}
