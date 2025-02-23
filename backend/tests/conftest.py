import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

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
