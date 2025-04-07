"""
Django settings for Retail Automation API project

Для production необходимо:
1. Установить DEBUG=False
2. Настроить SECRET_KEY из переменных окружения
3. Указать корректные ALLOWED_HOSTS
4. Настроить SSL/TLS
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()

# ==============================================================================
# Базовые настройки проекта
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = "orders.urls"
WSGI_APPLICATION = "orders.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
AUTH_USER_MODEL = "backend.User"
BACKEND_URL = "http://localhost"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ==============================================================================
# Безопасность
# ==============================================================================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-default-key-for-dev")
DEBUG = True
ALLOWED_HOSTS = ["*"]

# HTTPS settings (активировать для production)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ["https://localhost"]
CORS_ALLOW_ALL_ORIGINS = True
X_FRAME_OPTIONS = "SAMEORIGIN"

# ==============================================================================
# База данных
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": os.getenv("POSTGRES_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("POSTGRES_DB", "diploma_shop"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# ==============================================================================
# Приложения и middleware
# ==============================================================================

INSTALLED_APPS = [
    # JET Admin
    "jet.dashboard",
    "jet",
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "django_extensions",
    "drf_spectacular",
    "social_django",
    "cachalot",
    # Local
    "backend",
]
SITE_ID = 1
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==============================================================================
# Шаблоны и контекстные процессоры
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "backend/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
            ],
        },
    },
]

# ==============================================================================
# REST Framework
# ==============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "200/minute",
        "anon": "100/minute",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=100),
}

# ==============================================================================
# OpenAPI (drf-spectacular)
# ==============================================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Retail Automation API",
    "DESCRIPTION": "Сервис для автоматизации процессов интернет-магазина и розничной сети.\n\nПозволяет управлять товарами, заказами, поставщиками и клиентами через единое API.\n\nПоддерживает интеграцию с внешними системами, email-уведомления и аналитику продаж.\n\n\n[Панель администратора](http://localhost/admin/)\n\n[GitHub](https://github.com/jkeevk/diploma_shop)",
    "VERSION": "0.1.1",
    "CONTACT": {
        "name": "jkeevk@yandex.ru",
        "email": "jkeevk@yandex.ru",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api",
    "DEFAULT_AUTO_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "SWAGGER_UI_SETTINGS": {
        "filter": True,
    },
}

# ==============================================================================
# Аутентификация и авторизация
# ==============================================================================

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
)

SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

VK_APP_ID = os.getenv("VK_APP_ID")
VK_CLIENT_SECRET = os.getenv("VK_CLIENT_SECRET")
VK_REDIRECT_URI = "https://oauth.vk.com/blank.html"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["email", "profile"]

# ==============================================================================
# Локализация и время
# ==============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==============================================================================
# Статика и медиа
# ==============================================================================

STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ==============================================================================
# Email
# ==============================================================================

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Отключает отправку Email уведомлений во время запуска тестов
TESTING = os.getenv("DJANGO_TESTING", "False").lower() == "true"

# ==============================================================================
# Celery
# ==============================================================================

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_TASK_ALWAYS_EAGER = False

# ==============================================================================
# Логирование
# ==============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "debug.log",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# ==============================================================================
# Django JET Admin dashboard
# ==============================================================================

JET_THEMES = [
    {"theme": "default", "color": "#47bac1", "title": "Default"},
    {"theme": "green", "color": "#44b78b", "title": "Green"},
    {"theme": "light-green", "color": "#2faa60", "title": "Light Green"},
    {"theme": "light-violet", "color": "#a464c4", "title": "Light Violet"},
    {"theme": "light-blue", "color": "#5EADDE", "title": "Light Blue"},
    {"theme": "light-gray", "color": "#222", "title": "Light Gray"},
]

JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = True
JET_APP_INDEX_DASHBOARD = "jet.dashboard.dashboard.DefaultAppIndexDashboard"
JET_DASHBOARD_LAYOUT = "layout.VerticalLayout"
JET_INDEX_DASHBOARD = "backend.dashboard.CustomIndexDashboard"

JET_SIDE_MENU_ITEMS = [
    # Раздел управления пользователями
    {
        "label": "Управление доступом",
        "items": [
            {"name": "backend.user", "label": "Пользователи"},
            {"name": "auth.group", "label": "Группы доступа"},
        ],
    },
    # Раздел клиентских данных
    {
        "label": "Клиентские данные",
        "app_label": "backend",
        "items": [
            {"name": "contact", "label": "Контактные данные"},
            {"name": "order", "label": "История заказов"},
            {"name": "orderitem", "label": "Позиции заказов"},
        ],
    },
    # Раздел управления товарами
    {
        "label": "Товарный каталог",
        "app_label": "backend",
        "items": [
            {"name": "shop", "label": "Магазины"},
            {"name": "category", "label": "Категории товаров"},
            {"name": "product", "label": "Товарные карточки"},
            {"name": "productinfo", "label": "Детализация товаров"},
            {"name": "parameter", "label": "Характеристики"},
            {"name": "productparameter", "label": "Характеристики товаров"},
        ],
    },
    # Раздел управления магазинами
    {
        "label": "Операции поставщика",
        "items": [
            {
                "url": "/admin/price_update/",
                "label": "Обновить прайс",
                "permissions": ["partner.change_price"],
                "url_blank": False,
            }
        ],
    },
    # Раздел социальных сетей
    {
        "label": "Социальная авторизация",
        "items": [
            {"name": "social_django.usersocialauth", "label": "Привязанные аккаунты"},
            {"name": "social_django.nonce", "label": "Одноразовые коды"},
            {"name": "social_django.association", "label": "Ассоциации сессий"},
            {"name": "social_django.code", "label": "Коды авторизации"},
            {"name": "social_django.partial", "label": "Частичные данные"},
        ],
    },
]

# ==============================================================================
# Интеграции
# ==============================================================================

# Sentry (логирование ошибок)
SENTRY_DSN = os.getenv("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    send_default_pii=True,
)

# Cachalot (кэширования запросов к БД)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Silk (профилирование)
if DEBUG:
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE += ["silk.middleware.SilkyMiddleware"]
else:
    SILKY_ENABLE = False

SILKY_AUTHENTICATION = False
SILKY_AUTHORISATION = False
SILKY_IGNORE_PATHS = [
    r"/admin/",
    r"/silk/",
    r"/staticfiles/",
    r"/media/",
    r"/favicon.ico",
]
