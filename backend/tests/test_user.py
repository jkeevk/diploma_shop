import pytest
from django.urls import reverse
from rest_framework import status
from ..models import Category

@pytest.mark.django_db
class TestCategoryViewSet:
    """Тесты для CategoryViewSet, обеспечивающие проверку функциональности API категорий."""

    @pytest.fixture(autouse=True)
    def setup_method(self, api_client):
        """Настройка тестового клиента и создание тестовой категории перед каждым тестом."""
        self.client = api_client
        self.category = Category.objects.create(name="Test Category")
        self.url = reverse('categories')

    def test_list_categories(self):
        """Проверка получения списка категорий."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1, "Expected one category in the response."

    def test_retrieve_category(self):
        """Проверка получения конкретной категории по её ID."""
        response = self.client.get(self.url)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        
        categories = response.json()
        assert len(categories) > 0, "Expected at least one category in the response."
        assert categories[0]['name'] == 'Test Category', f"Expected category name to be 'Test Category', got {categories[0]['name']}"
        