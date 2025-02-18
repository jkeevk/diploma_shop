from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from backend.views import (
    UserViewSet,
    ProductViewSet,
    RegisterView,
    ConfirmRegistrationView,
    CategoryView,
    ShopView,
    ContactViewSet,
    PartnerUpdateView,
    OrderViewSet,
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
    LoginView
)


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet)
router.register(r"users", UserViewSet, basename="user")
router.register(r"contacts", ContactViewSet, basename="user-contacts")

user_router = NestedDefaultRouter(router, r"users", lookup="user")
user_router.register(r"contacts", ContactViewSet, basename="user-contacts")

urlpatterns = (
    [
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('user/login/', LoginView.as_view(), name='login'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path("admin/", admin.site.urls),
        path("", include(router.urls)),
        path("", include(user_router.urls)),
        path("user/register/", RegisterView.as_view(), name="user-register"),
        path(
            "user/register/confirm/<str:token>/",
            ConfirmRegistrationView.as_view(),
            name="user-register-confirm",
        ),
        path(
            "user/password_reset/",
            PasswordResetView.as_view(),
            name="password_reset",
        ),
        path(
            "user/password_reset/confirm/<uidb64>/<token>/",
            PasswordResetConfirmView.as_view(),
            name="password_reset_confirm",
        ),
        path("partner/update/", PartnerUpdateView.as_view(), name="partner-update"),
        path("categories/", CategoryView.as_view(), name="categories"),
        path("shops/", ShopView.as_view(), name="shops"),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )