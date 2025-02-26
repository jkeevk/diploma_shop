import pytest
from django.db import IntegrityError
from rest_framework.test import APIClient
from backend.models import (
    Category, Shop, Product, User, ProductInfo, Parameter, ProductParameter
)

@pytest.mark.django_db
class TestProductParameter:
    """
    Тесты для модели ProductParameter.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_product_parameter(self):
        """
        Тест создания параметра товара.
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

        parameter = Parameter.objects.create(
            name="Test Parameter",
        )

        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        assert product_parameter.product_info == product_info
        assert product_parameter.parameter == parameter
        assert product_parameter.value == "Test Value"

    def test_update_product_parameter(self):
        """
        Тест обновления параметра товара.
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

        parameter = Parameter.objects.create(
            name="Test Parameter",
        )

        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        product_parameter.value = "Updated Value"
        product_parameter.save()

        assert product_parameter.value == "Updated Value"

    def test_delete_product_parameter(self):
        """
        Тест удаления параметра товара.
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

        parameter = Parameter.objects.create(
            name="Test Parameter",
        )

        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        product_parameter_id = product_parameter.id
        product_parameter.delete()

        assert not ProductParameter.objects.filter(id=product_parameter_id).exists()

    def test_create_product_parameter_without_required_fields(self):
        """
        Тест создания параметра товара без обязательных полей.
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

        parameter = Parameter.objects.create(
            name="Test Parameter",
        )

        with pytest.raises(Exception):
            ProductParameter.objects.create(
                parameter=parameter,
                value="Test Value",
            )

    def test_create_duplicate_product_parameter(self):
        """
        Тест создания дубликата параметра товара.
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

        parameter = Parameter.objects.create(
            name="Test Parameter",
        )

        ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        with pytest.raises(IntegrityError):
            ProductParameter.objects.create(
                product_info=product_info,
                parameter=parameter,
                value="Test Value",
            )
