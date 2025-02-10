from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from backend.views import (
    ProductViewSet, 
    UserViewSet, 
    CategoryViewSet, 
    ShopViewSet, 
    ContactViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'users', UserViewSet)
router.register(r'shops', ShopViewSet)

user_router = NestedDefaultRouter(router, r'users', lookup='user')
user_router.register(r'contacts', ContactViewSet, basename='user-contacts')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(user_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)