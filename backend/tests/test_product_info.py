import pytest
from rest_framework.test import APIClient
from backend.models import ProductInfo, Product, Shop


@pytest.mark.django_db
class TestProductInfoModel:
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
        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
        )
        shop = Shop.objects.create(
            name="Test Shop",
            url="http://example.com",
        )
        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )
        assert product_info.product == product
        assert product_info.shop == shop
        assert product_info.quantity == 10
        assert product_info.price == 100.00
        assert product_info.price_rrc == 120.00
