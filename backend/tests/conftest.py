import pytest
import redis
from django.contrib.auth import get_user_model
from django.conf import settings
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
    User,
)
from backend.admin import UserAdmin, ProductParameterAdmin, OrderAdmin, OrderItemAdmin
from django.contrib.admin.sites import AdminSite
import uuid

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для создания тестового клиента API."""
    return APIClient()


@pytest.fixture
def redis_client():
    """
    Фикстура для создания клиента Redis.
    """
    return redis.Redis(
        host="redis",
        port=6379,
        db=2,
        socket_timeout=3,
    )


@pytest.fixture
def user_factory():
    """
    Фикстура для создания пользователей с заданными параметрами.
    Возвращает функцию, которая создает пользователя с заданными параметрами.
    """

    def create_user(role, email=None, is_active=True, **extra_fields):
        """
        Создает пользователя с заданными параметрами.
        """
        email = email or f"example-{uuid.uuid4()}@example.com"
        return User.objects.create_user(
            email=email,
            password="strongpassword123",
            first_name="User",
            last_name="User",
            role=role,
            is_active=is_active,
            **extra_fields,
        )

    return create_user


@pytest.fixture
def supplier(user_factory):
    """Фикстура для создания поставщика."""
    return user_factory(role="supplier")


@pytest.fixture
def admin(user_factory):
    """Фикстура для создания администратора."""
    return user_factory(role="admin")


@pytest.fixture
def customer(user_factory):
    """Фикстура для создания клиента."""
    return user_factory(role="customer")


@pytest.fixture
def customer_login():
    """Фикстура для клиента для теста авторизации."""
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
        name="Supplier Shop", url="http://supplier.com", user=supplier
    )


@pytest.fixture
def product(category):
    """Фикстура для создания продукта."""
    return Product.objects.create(
        name="Test Product", model="Test Model", category=category
    )


@pytest.fixture
def another_product(category):
    """Фикстура для создания другого продукта."""
    return Product.objects.create(
        name="Test2 Product", model="Test2 Model", category=category
    )


@pytest.fixture
def product_parameter(product_info, parameter):
    """Фикстура для создания параметра продукта."""
    return ProductParameter.objects.create(
        product_info=product_info, parameter=parameter, value="Test Value"
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
def another_user_contact(customer_login):
    """Фикстура для создания контакта другого пользователя."""
    return Contact.objects.create(
        user=customer_login,
        city="SPb",
        street="Nevsky",
        house="120",
        structure="1",
        building="B",
        apartment="12",
        phone="+79991234567",
    )


@pytest.fixture
def order_item(customer, product, shop):
    """Фикстура для создания элемента заказа."""
    product_info = ProductInfo.objects.create(
        product=product, shop=shop, quantity=10, price=100, price_rrc=120
    )
    order = Order.objects.create(user=customer, status="new")
    return OrderItem.objects.create(order=order, product=product, shop=shop, quantity=3)


@pytest.fixture
def shops(user_factory):
    """Фикстура для создания нескольких магазинов с разными поставщиками."""
    supplier1 = user_factory(role="supplier", email="supplier_1@example.com")
    supplier2 = user_factory(role="supplier", email="supplier_2@example.com")
    return [
        Shop.objects.create(name="Shop #1", user=supplier1),
        Shop.objects.create(name="Shop #2", user=supplier2),
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
    """Фикстура для создания параметра."""
    return Parameter.objects.create(name="Test Parameter")


@pytest.fixture
def old_parameter():
    """Фикстура для старого параметра."""
    return Parameter.objects.create(name="Old Parameter")


@pytest.fixture
def deletable_parameter():
    """Фикстура для параметра, который будет удален."""
    return Parameter.objects.create(name="Parameter to delete")


@pytest.fixture
def user_admin():
    admin_site = AdminSite()
    return UserAdmin(User, admin_site)


@pytest.fixture
def sample_user():
    return User.objects.create_user(
        email="test@example.com",
        password="initial_password",
        first_name="John",
        last_name="Doe",
    )


@pytest.fixture
def product_parameter_admin(user_admin):
    """Фикстура для создания экземпляра ProductParameterAdmin."""
    return ProductParameterAdmin(ProductParameter, user_admin)


@pytest.fixture
def order_admin(user_admin):
    """Фикстура для создания экземпляра OrderAdmin."""
    return OrderAdmin(Order, user_admin)


@pytest.fixture
def order_item_admin(user_admin):
    """Фикстура для создания экземпляра OrderItemAdmin."""
    return OrderItemAdmin(OrderItem, user_admin)


@pytest.fixture
def order_with_multiple_shops(db, customer, shops, product, another_product):
    """Фикстура для создания заказа с товарами из разных магазинов"""
    order = Order.objects.create(user=customer)
    OrderItem.objects.create(order=order, product=product, shop=shops[0], quantity=2)
    OrderItem.objects.create(
        order=order, product=another_product, shop=shops[1], quantity=3
    )

    return order


@pytest.fixture(autouse=True)
def disable_throttling(request):
    marker = request.node.get_closest_marker("throttling")
    if not marker:
        original_throttle_classes = settings.REST_FRAMEWORK.get(
            "DEFAULT_THROTTLE_CLASSES", []
        )
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
        yield
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = original_throttle_classes
    else:
        yield
