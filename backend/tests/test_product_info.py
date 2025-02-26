import pytest
from rest_framework.test import APIClient
from backend.models import (
    Category, Shop, Product, User, ProductInfo
)
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class TestProductInfo:
    """
    Тесты для модели ProductInfo.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_product_info(self):
        """
        Тест создания информации о товаре.
        """
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

        assert product_info.product == product
        assert product_info.shop == shop
        assert product_info.description == "Test Description"
        assert product_info.quantity == 10
        assert product_info.price == 100.00
        assert product_info.price_rrc == 120.00

    def test_product_info_unique_together(self):
        """
        Тест, проверяющий уникальность сочетания продукта и магазина в ProductInfo.
        """
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

        product_info1 = ProductInfo.objects.create(
            product=product,
            shop=shop,
            description="Test Description 1",
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        with pytest.raises(Exception):
            ProductInfo.objects.create(
                product=product,
                shop=shop,
                description="Test Description 2",
                quantity=20,
                price=200.00,
                price_rrc=220.00,
            )

    def test_product_info_price_validation(self):
        """
        Тест для проверки валидации цены.
        """
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

        with pytest.raises(ValidationError):
            product_info = ProductInfo(
                product=product,
                shop=shop,
                description="Test Description",
                quantity=10,
                price=-100.00,
                price_rrc=120.00,
            )
            product_info.clean()

    def test_product_info_quantity_validation(self):
        """
        Тест для проверки валидации количества.
        """
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

        with pytest.raises(ValidationError):
            product_info = ProductInfo(
                product=product,
                shop=shop,
                description="Test Description",
                quantity=-10,
                price=100.00,
                price_rrc=120.00,
            )
            product_info.clean()

    def test_product_info_str_method(self):
        """
        Тест метода __str__ модели ProductInfo.
        """
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

        assert str(product_info) == "Test Description (Supplier Shop)"
