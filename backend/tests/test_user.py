import pytest
from django.urls import reverse
from rest_framework import status
from ..models import Category

@pytest.mark.django_db
class TestCategoryViewSet:

    @pytest.fixture(autouse=True)
    def setup_method(self, api_client):
        self.client = api_client
        self.category = Category.objects.create(name="Test Category")
        self.url = reverse('categories')

        
    def test_list_categories(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1, "Expected one category in the response."


    def test_retrieve_category(self):
        response = self.client.get(self.url)
        assert response.status_code == 200, "Expected status code 200, got {response.status_code}"
        
        categories = response.json()
        assert len(categories) > 0, "Expected at least one user in the response."
        assert categories[0]['name'] == 'Test Category', "Expected category name to be 'Test Category', got {categories[0]['name']}"
