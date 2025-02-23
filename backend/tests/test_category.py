import pytest
from rest_framework.test import APIClient
from backend.models import Category


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

    def test_create_category(self):
        """
        Тест создания категории.
        """
        category = Category.objects.create(
            name="Test Category",
        )
        assert category.name == "Test Category"
