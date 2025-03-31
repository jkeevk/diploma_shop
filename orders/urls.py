"""
URL конфигурация для проекта Django.

Этот файл определяет маршруты для API, включая маршруты для пользователей, продуктов,
категорий, магазинов и других связанных ресурсов. Он также включает маршруты для
документации API с использованием drf-spectacular.

"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import RedirectView
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

import backend.views as views
import backend.OAuth.social_views as social_views
import backend.tests.views_tests as tests_views

from backend.admin import admin_site

# API Router Configuration
api_router = DefaultRouter()
api_router.register(r"products", views.ProductViewSet, basename="product")
api_router.register(r"users", views.UserViewSet, basename="user")
api_router.register(r"contacts", views.ContactViewSet, basename="user-contacts")
api_router.register(r"basket", views.BasketViewSet, basename="basket")
api_router.register(r"categories", views.CategoryViewSet, basename="category")
api_router.register(r"parameters", views.ParameterViewSet, basename="parameter")

# Nested Routes
user_router = NestedDefaultRouter(api_router, r"users", lookup="user")
user_router.register(r"contacts", views.ContactViewSet, basename="user-contacts")

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url="/api/docs/swagger", permanent=False),
        name="root-redirect",
    ),
    path("admin/", admin_site.urls),
    # API Documentation
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    # Authentication Endpoints
    path(
        "api/auth/",
        include(
            [
                path("login", views.LoginView.as_view(), name="login"),
                path("register", views.RegisterView.as_view(), name="register"),
                path(
                    "register/confirm/<str:token>",
                    views.ConfirmRegistrationView.as_view(),
                    name="register-confirm",
                ),
                path(
                    "password/reset",
                    views.PasswordResetView.as_view(),
                    name="password-reset",
                ),
                path(
                    "password/reset/confirm/<str:uidb64>/<str:token>",
                    views.PasswordResetConfirmView.as_view(),
                    name="password-reset-confirm",
                ),
                path("social/vk", views.VKAuthView.as_view(), name="vk-auth"),
            ]
        ),
    ),
    # Social Auth Endpoints
    path(
        "social/",
        include(
            [
                path(
                    "google/login", social_views.google_login_page, name="google-login"
                ),
                path("google/auth", social_views.google_auth, name="google-auth"),
                path(
                    "google/callback",
                    social_views.google_callback,
                    name="google-callback",
                ),
                path("", include("social_django.urls", namespace="social")),
            ]
        ),
    ),
    # Partner API Endpoints
    path(
        "api/partner/",
        include(
            [
                path(
                    "update", views.PartnerUpdateView.as_view(), name="partner-update"
                ),
                path(
                    "import", views.PartnerImportView.as_view(), name="partner-import"
                ),
                path(
                    "import/status/<str:task_id>",
                    views.PartnerImportStatusView.as_view(),
                    name="import-status",
                ),
                path("orders", views.PartnerOrders.as_view(), name="partner-orders"),
            ]
        ),
    ),
    # User Management Endpoints
    path(
        "api/user/",
        include(
            [
                path(
                    "<int:user_id>/toggle-activity",
                    views.ToggleUserActivityView.as_view(),
                    name="toggle-user-activity",
                ),
                path("orders", views.UserOrdersView.as_view(), name="user-orders"),
            ]
        ),
    ),
    # Shop & Order Endpoints
    path("api/shops", views.ShopView.as_view(), name="shops"),
    path(
        "api/basket/confirm/<int:contact_id>",
        views.ConfirmBasketView.as_view(),
        name="confirm-basket",
    ),
    # Testing Endpoints
    path(
        "api/tests/",
        include(
            [
                path(
                    "run-pytest", tests_views.RunPytestView.as_view(), name="run-pytest"
                ),
                path(
                    "check-pytest/<str:task_id>",
                    tests_views.CheckPytestTaskView.as_view(),
                    name="check-pytest",
                ),
                path(
                    "trigger-error",
                    tests_views.ForceSentryErrorAPIView.as_view(),
                    name="trigger-error",
                ),
            ]
        ),
    ),
    # Third-party Integrations
    path("jet/", include("jet.urls", "jet")),
    path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
    path("silk/", include("silk.urls", "silk")),
    # Main API Routes
    path("api/", include(api_router.urls)),
    path("api/", include(user_router.urls)),
]

# Static and media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug Toolbar
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
