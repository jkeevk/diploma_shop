import pytest
from rest_framework.test import APIClient
from backend.models import (
    Category, Shop, Product, User, Order, OrderItem, ProductInfo, Parameter, ProductParameter
)
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestCategoryModel:
    """
    Тесты для модели Category.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_product_and_shop_with_supplier(self):
        """
        Тест создания товара и магазина, связанного с поставщиком.
        """
        supplier = User.objects.create_user(
            email="supplier@example.com",
            password="strongpassword123",
            first_name="Supplier",
            last_name="User",
            role="supplier",
            is_active=True
        )

        self.client.force_authenticate(user=supplier)

        data = {
            "name": "Supplier Shop",
            "url": "http://supplier.com",
        }
        url = reverse("shops")
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        shop = Shop.objects.get(user=supplier)
        assert shop.name == "Supplier Shop"
        assert shop.url == "http://supplier.com"
        assert shop.user == supplier

        category = Category.objects.create(
            name="Test Category",
        )
        assert category.name == "Test Category"

        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=category,
        )
        assert product.name == "Test Product"
        assert product.model == "Test Model"
        assert product.category == category

        parameter = Parameter.objects.create(
            name="Test Parameter",
        )
        assert parameter.name == "Test Parameter"

        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            description="Test Description",
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )
        assert product_info.product == product
        assert product_info.shop == shop
        assert product_info.quantity == 10
        assert product_info.price == 100.00

        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )
        assert product_parameter.product_info == product_info
        assert product_parameter.parameter == parameter
        assert product_parameter.value == "Test Value"

    def test_add_product_to_basket(self):
        """
        Тест добавления товара в корзину.
        """
        customer = User.objects.create_user(
            email="customer@example.com",
            password="strongpassword123",
            first_name="Customer",
            last_name="User",
            role="customer",
            is_active=True
        )

        self.client.force_authenticate(user=customer)

        supplier = User.objects.create_user(
            email="supplier@example.com",
            password="strongpassword123",
            first_name="Supplier",
            last_name="User",
            role="supplier",
            is_active=True
        )
        shop = Shop.objects.create(
            name="Supplier Shop",
            url="http://supplier.com",
            user=supplier,
        )

        category = Category.objects.create(
            name="Test Category",
        )

        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=category,
        )

        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            description="Test Description",
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        order = Order.objects.create(
            user=customer,
            status="new",
        )

        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            shop=shop,
            quantity=2,
        )

        assert order_item.order == order
        assert order_item.product == product
        assert order_item.shop == shop
        assert order_item.quantity == 2
        assert order.total_cost() == 200.00