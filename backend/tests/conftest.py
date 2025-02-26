import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from backend.models import Category, Shop, Product

User = get_user_model()

@pytest.fixture
def api_client():
    """Фикстура для создания тестового клиента API.

    Возвращает экземпляр APIClient, который можно использовать для
    выполнения запросов к API в тестах.
    """
    return APIClient()

@pytest.fixture
def supplier():
    """Фикстура для создания пользователя- поставщика."""
    return User.objects.create_user(
        email="supplier@example.com",
        password="strongpassword123",
        first_name="Supplier",
        last_name="User",
        role="supplier",
        is_active=True
    )

@pytest.fixture
def admin():
    """Фикстура для создания пользователя- администратора."""
    return User.objects.create_user(
        email="admin@example.com",
        password="strongpassword123",
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True
    )

@pytest.fixture
def customer():
    """Фикстура для создания пользователя- клиента."""
    return User.objects.create_user(
        email="customer@example.com",
        password="strongpassword123",
        first_name="Customer",
        last_name="User",
        role="customer",
        is_active=True
    )

@pytest.fixture
def category():
    """Фикстура для создания категории."""
    return Category.objects.create(name="Test Category")

@pytest.fixture
def shop(supplier):
    """Фикстура для создания магазина."""
    return Shop.objects.create(
        name="Supplier Shop",
        url="http://supplier.com",
        user=supplier,
    )

@pytest.fixture
def product(category):
    """Фикстура для создания продукта."""
    return Product.objects.create(
        name="Test Product",
        model="Test Model",
        category=category,
    )
