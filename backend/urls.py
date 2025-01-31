from django.contrib import admin
from django.urls import path
from .views import ProductViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', ProductViewSet.as_view(), name='products'),
    path('products/<int:pk>/', ProductViewSet.as_view(), name='product'),
]
