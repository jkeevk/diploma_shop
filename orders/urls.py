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
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from backend.views import (
    UserViewSet,
    ProductViewSet,
    RegisterView,
    ConfirmRegistrationView,
    CategoryViewSet,
    ShopView,
    ContactViewSet,
    PartnerUpdateView,
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
    BasketViewSet,
    PartnerOrders,
    PartnerImportView,
    PartnerImportStatusView,
    ConfirmBasketView,
    ToggleUserActivityView,
    ParameterViewSet,
    UserOrdersView,
    VKAuthView,
)
from backend.tests.views_tests import (
    RunPytestView,
    CheckPytestTaskView,
    ForceSentryErrorAPIView,
)
from backend.admin import admin_site

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"users", UserViewSet, basename="user")
router.register(r"contacts", ContactViewSet, basename="user-contacts")
router.register(r"basket", BasketViewSet, basename="basket")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"parameters", ParameterViewSet, basename="parameter")

user_router = NestedDefaultRouter(router, r"users", lookup="user")
user_router.register(r"contacts", ContactViewSet, basename="user-contacts")

urlpatterns = (
    [
        path("schema", SpectacularAPIView.as_view(), name="schema"),
        path(
            "swagger",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path("user/login", LoginView.as_view(), name="login"),
        path("vk-auth/", VKAuthView.as_view(), name="vk_auth"),
        path("redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
        path(r"jet/", include("jet.urls", "jet")),
        path(r"jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
        path("admin/", admin_site.urls, name="admin"),
        path("tests/run-pytest/", RunPytestView.as_view(), name="run-pytest"),
        path(
            "tests/trigger-error/",
            ForceSentryErrorAPIView.as_view(),
            name="trigger-error",
        ),
        path(
            "tests/check-pytest-task/<str:task_id>/",
            CheckPytestTaskView.as_view(),
            name="check_pytest_task",
        ),
        path("", include(router.urls)),
        path("", include(user_router.urls)),
        path("user/register", RegisterView.as_view(), name="user-register"),
        path(
            "user/register/confirm/<str:token>",
            ConfirmRegistrationView.as_view(),
            name="user-register-confirm",
        ),
        path(
            "user/password_reset",
            PasswordResetView.as_view(),
            name="password-reset",
        ),
        path(
            "user/password_reset/confirm/<str:uidb64>/<str:token>",
            PasswordResetConfirmView.as_view(),
            name="password_reset_confirm",
        ),
        path("partner/update", PartnerUpdateView.as_view(), name="partner-update"),
        path("partner/import", PartnerImportView.as_view(), name="partner-import"),
        path(
            "partner/import/status/<str:task_id>/",
            PartnerImportStatusView.as_view(),
            name="import-status",
        ),
        path(
            "basket/confirm/<int:contact_id>/",
            ConfirmBasketView.as_view(),
            name="confirm-basket",
        ),
        path("partner/orders", PartnerOrders.as_view(), name="partner-orders"),
        path("shops", ShopView.as_view(), name="shops"),
        path(
            "user/<int:user_id>/toggle-activity/",
            ToggleUserActivityView.as_view(),
            name="toggle-user-activity",
        ),
        path("user/orders", UserOrdersView.as_view(), name="user-orders"),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
