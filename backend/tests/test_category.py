import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Category


@pytest.mark.django_db
class TestCategoryViewSet:
    """
    Тесты для CategoryViewSet.
    """

    def test_list_categories_unauthenticated(self, api_client, category):
        """
        Тест получения списка категорий неавторизованным пользователем.
        """
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Category"

    def test_create_category_as_admin(self, api_client, admin):
        """
        Тест создания категории администратором.
        """
        api_client.force_authenticate(user=admin)

        data = {"name": "New Category"}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name="New Category").exists()

    def test_create_category_as_customer(self, api_client, customer):
        """
        Тест создания категории пользователем с ролью customer.
        Должен вернуть ошибку 403.
        """
        api_client.force_authenticate(user=customer)

        data = {"name": "New Category"}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(response.data["detail"])

    def test_update_category_as_admin(self, api_client, admin, category):
        """
        Тест обновления категории администратором.
        """
        api_client.force_authenticate(user=admin)

        data = {"name": "Updated Category"}
        url = reverse("category-detail", args=[category.id])
        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == "Updated Category"

    def test_update_category_as_customer(self, api_client, customer, category):
        """
        Тест обновления категории пользователем с ролью customer.
        Должен вернуть ошибку 403.
        """
        api_client.force_authenticate(user=customer)

        data = {"name": "Updated Category"}
        url = reverse("category-detail", args=[category.id])
        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(response.data["detail"])

    def test_delete_category_as_admin(self, api_client, admin, category):
        """
        Тест удаления категории администратором.
        """
        api_client.force_authenticate(user=admin)

        url = reverse("category-detail", args=[category.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()

    def test_delete_category_as_customer(self, api_client, customer, category):
        """
        Тест удаления категории пользователем с ролью customer.
        Должен вернуть ошибку 403.
        """
        api_client.force_authenticate(user=customer)

        url = reverse("category-detail", args=[category.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(response.data["detail"])

    def test_category_str_method(self, category):
        """
        Тест метода __str__ модели Category.
        """
        assert str(category) == "Test Category"
