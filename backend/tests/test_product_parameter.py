import pytest
from rest_framework.test import APIClient
from backend.models import ProductParameter, ProductInfo, Parameter, Shop, Product


@pytest.mark.django_db
class TestProductParameterModel:
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
        product_info = ProductInfo.objects.create(
            product=Product.objects.create(name="Test Product"),
            shop=Shop.objects.create(name="Test Shop"),
            quantity=10,
            price=100.00,
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
