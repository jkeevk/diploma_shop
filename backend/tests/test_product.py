import pytest
from rest_framework.test import APIClient
from backend.models import Product, Category


@pytest.mark.django_db
class TestProductModel:
    """
    Тесты для модели Product.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_product(self):
        """
        Тест создания товара.
        """
        category = Category.objects.create(
            name="Test Category",
        )
        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=category,
        )
        assert product.name == "Test Product"
        assert product.model == "Test Model"
        assert product.category == category
