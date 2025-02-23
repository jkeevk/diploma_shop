import pytest
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
