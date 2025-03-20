import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from backend.models import (
    Category,
    Shop,
    Product,
    Contact,
    ProductInfo,
    OrderItem,
    Order,
)

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
    """Фикстура для создания пользователя - поставщика."""
    return User.objects.create_user(
        email="supplier@example.com",
        password="strongpassword123",
        first_name="Supplier",
        last_name="User",
        role="supplier",
        is_active=True,
    )


@pytest.fixture
def admin():
    """Фикстура для создания пользователя - администратора."""
    return User.objects.create_user(
        email="admin@example.com",
        password="strongpassword123",
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True,
    )


@pytest.fixture
def customer():
    """Фикстура для создания пользователя - клиента."""
    return User.objects.create_user(
        email="customer@example.com",
        password="strongpassword123",
        first_name="Customer",
        last_name="User",
        role="customer",
        is_active=True,
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


@pytest.fixture
def another_product(category):
    """Фикстура для создания 2 продукта."""
    return Product.objects.create(
        name="Test2 Product",
        model="Test2 Model",
        category=category,
    )


@pytest.fixture
def contact(customer):
    """Фикстура для создания контакта пользователя."""
    return Contact.objects.create(
        user=customer,
        city="Moscow",
        street="Lenina",
        house="10",
        structure="1",
        building="A",
        apartment="15",
        phone="+79991234567",
    )


@pytest.fixture
def order_item(customer, product, shop):
    """Фикстура для создания заказа."""
    ProductInfo.objects.create(
        product=product, shop=shop, quantity=10, price=100, price_rrc=120
    )
    order = Order.objects.create(user=customer, status="new")
    return OrderItem.objects.create(order=order, product=product, shop=shop, quantity=3)


@pytest.fixture
def shops(supplier):
    """Фикстура для создания магазинов."""
    return [
        Shop.objects.create(name="Shop 1", user=supplier),
        Shop.objects.create(name="Shop 2", user=supplier),
    ]


@pytest.fixture
def product_info(product, shop):
    """Фикстура для создания информации о товаре в магазине."""
    return ProductInfo.objects.create(
        product=product, shop=shop, quantity=10, price=100, price_rrc=120
    )


@pytest.fixture
def order(customer, product, shop, product_info):
    """Фикстура для создания заказа с одним товаром."""
    order = Order.objects.create(user=customer)
    OrderItem.objects.create(order=order, product=product, shop=shop, quantity=2)
    return order


@pytest.fixture
def other_customer():
    """Фикстура для создания пользователя - клиента."""
    return User.objects.create_user(
        email="customer2@example.com",
        password="strongpassword1234",
        first_name="Customer",
        last_name="User",
        role="customer",
        is_active=True,
    )
