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

# ==============================================================================
# Безопасность
# ==============================================================================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-default-key-for-dev")
DEBUG = True
ALLOWED_HOSTS = ["*"]

# HTTPS settings (активировать для production)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
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
        "user": "500/minute",
        "anon": "300/minute",
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
    "TAGS": [
        {
            "name": "user",
        },
    ],
}

# ==============================================================================
# Аутентификация и авторизация
# ==============================================================================

AUTHENTICATION_BACKENDS = (
    "social_core.backends.vk.VKOAuth2",
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
MEDIA_ROOT = BASE_DIR / "media"

# ==============================================================================
# Email
# ==============================================================================

EMAIL_HOST = os.getenv("EMAIL_HOST", "user@user.user")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "smtp.yandex.ru")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "123")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

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
# JET Admin
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

# VK Auth (аутентификация ВК)
VK_APP_ID = os.getenv("VK_APP_ID")
VK_CLIENT_SECRET = os.getenv("VK_CLIENT_SECRET")
VK_REDIRECT_URI = "https://oauth.vk.com/blank.html"

# Cachalot (кэширования запросов к БД)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
