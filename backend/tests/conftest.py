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
    Parameter,
    ProductParameter,
)
import uuid

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для создания тестового клиента API.

    Возвращает экземпляр APIClient, который можно использовать для
    выполнения запросов к API в тестах.
    """
    return APIClient()


@pytest.fixture
def user_factory():
    """
    Фикстура для создания пользователей.

    Возвращает функцию, которая создает пользователя с заданными параметрами.
    """

    def create_user(role, email=None):
        """
        Создает пользователя с заданными параметрами.
        """
        return User.objects.create_user(
            email=email or f"example-{uuid.uuid4()}@example.com",
            password="strongpassword123",
            first_name="User",
            last_name="User",
            role=role,
            is_active=True,
        )

    return create_user


@pytest.fixture
def supplier(user_factory):
    """
    Фикстура для создания пользователя-поставщика.
    """
    return user_factory(role="supplier")


@pytest.fixture
def admin(user_factory):
    """
    Фикстура для создания пользователя-администратора.
    """
    return user_factory(role="admin")


@pytest.fixture
def customer(user_factory):
    """
    Фикстура для создания пользователя-клиента.
    """
    return user_factory(role="customer")


@pytest.fixture
def customer_login():
    """Фикстура для создания пользователя - клиента для теста авторизации."""
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
def product_parameter(product_info, parameter):
    """Фикстура для создания параметра продукта."""
    return ProductParameter.objects.create(
        product_info=product_info,
        parameter=parameter,
        value="Test Value",
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
def parameter():
    """Базовая фикстура для параметра"""
    return Parameter.objects.create(name="Test Parameter")


@pytest.fixture
def old_parameter():
    """Фикстура для параметра с именем 'Old Parameter'"""
    return Parameter.objects.create(name="Old Parameter")


@pytest.fixture
def deletable_parameter():
    """Фикстура для параметра который будем удалять"""
    return Parameter.objects.create(name="Parameter to delete")
