import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Category
from backend.views import CategoryViewSet
from rest_framework.request import Request
from unittest.mock import Mock


@pytest.mark.django_db
class TestCategoryViewSet:
    """
    Тесты для CategoryViewSet.
    Проверка различных сценариев работы с категориями:
    - Получение списка категорий.
    - Создание, обновление и удаление категорий.
    - Проверка прав доступа пользователей с разными ролями.
    - Валидация данных.
    """

    def test_list_categories_unauthenticated(self, api_client, category):
        """
        Тест: Получение списка категорий неавторизованным пользователем.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Один элемент в списке категорий с именем 'Test Category'.
        """
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Category"

    def test_create_category_as_admin(self, api_client, admin):
        """
        Тест: Создание категории администратором.

        Ожидаемый результат:
        - Статус ответа 201 (Created).
        - Новая категория создана в базе данных.
        """
        api_client.force_authenticate(user=admin)

        data = {"name": "New Category"}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name="New Category").exists()

    def test_create_duplicate_category_as_admin(self, api_client, admin):
        """
        Тест: Попытка создания категории с дублирующимся именем администратором.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке: 'Категория с таким именем уже существует'.
        """
        api_client.force_authenticate(user=admin)

        data = {"name": "New Category"}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name="New Category").exists()

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Категория с таким именем уже существует" == response.data["name"][0]

    def test_create_category_as_customer(self, api_client, customer):
        """
        Тест: Попытка создания категории пользователем с ролью 'customer'.

        Ожидаемый результат:
        - Статус ответа 403 (Forbidden).
        - Сообщение об ошибке: 'У вас недостаточно прав для выполнения этого действия.'.
        """
        api_client.force_authenticate(user=customer)

        data = {"name": "New Category"}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(
            response.data["detail"]
        )

    def test_create_category_unauthenticated(self, api_client):
        """
        Тест: Попытка создания категории неавторизованным пользователем.

        Ожидаемый результат:
        - Статус ответа 401 (Unauthorized).
        """
        data = {"name": "New Category"}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_category_invalid_data(self, api_client, admin):
        """
        Тест: Попытка создания категории с некорректными данными (пустое название).

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке: 'name' не может быть пустым.
        """
        api_client.force_authenticate(user=admin)

        data = {"name": ""}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_update_category_as_admin(self, api_client, admin, category):
        """
        Тест: Обновление категории администратором.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Имя категории обновляется на 'Updated Category'.
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
        Тест: Попытка обновления категории пользователем с ролью 'customer'.

        Ожидаемый результат:
        - Статус ответа 403 (Forbidden).
        - Сообщение об ошибке: 'У вас недостаточно прав для выполнения этого действия.'.
        """
        api_client.force_authenticate(user=customer)

        data = {"name": "Updated Category"}
        url = reverse("category-detail", args=[category.id])
        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(
            response.data["detail"]
        )

    def test_update_category_unauthenticated(self, api_client, category):
        """
        Тест: Попытка обновления категории неавторизованным пользователем.

        Ожидаемый результат:
        - Статус ответа 401 (Unauthorized).
        """
        data = {"name": "Updated Category"}
        url = reverse("category-detail", args=[category.id])
        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_category_as_admin(self, api_client, admin, category):
        """
        Тест: Удаление категории администратором.

        Ожидаемый результат:
        - Статус ответа 204 (No Content).
        - Категория удалена из базы данных.
        """
        api_client.force_authenticate(user=admin)

        url = reverse("category-detail", args=[category.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()

    def test_delete_category_as_customer(self, api_client, customer, category):
        """
        Тест: Попытка удаления категории пользователем с ролью 'customer'.

        Ожидаемый результат:
        - Статус ответа 403 (Forbidden).
        - Сообщение об ошибке: 'У вас недостаточно прав для выполнения этого действия.'.
        """
        api_client.force_authenticate(user=customer)

        url = reverse("category-detail", args=[category.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(
            response.data["detail"]
        )

    def test_delete_category_unauthenticated(self, api_client, category):
        """
        Тест: Попытка удаления категории неавторизованным пользователем.

        Ожидаемый результат:
        - Статус ответа 401 (Unauthorized).
        """
        url = reverse("category-detail", args=[category.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_category_str_method(self, category):
        """
        Тест метода __str__ модели Category.

        Ожидаемый результат:
        - Метод __str__ возвращает название категории.
        """
        assert str(category) == "Test Category"

    def test_category_unique_name(self, api_client, admin):
        """
        Тест: Проверка уникальности названия категории.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке: 'Категория с таким именем уже существует'.
        """
        api_client.force_authenticate(user=admin)

        category1 = Category.objects.create(name="Unique Category")

        data = {"name": "Unique Category"}
        url = reverse("category-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        assert "Категория с таким именем уже существует" in str(response.data["name"])

    def test_category_search(self, api_client, category):
        """
        Тест: Поиск категорий по имени.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Один элемент в списке категорий, название 'Test Category'.
        """
        url = reverse("category-list") + "?search=Test"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Category"

    def test_category_permission_for_non_action(self):
        """
        Тест: Проверка прав доступа для действия, не определенного в CategoryViewSet.

        Ожидаемый результат:
        - Получение пустого списка прав доступа (для несуществующего действия).
        """
        view = CategoryViewSet()
        view.action = "non_action"
        view.request = Mock(spec=Request)
        permissions = view.get_permissions()
        assert permissions == []

    def test_get_nonexistent_category(self, api_client, admin):
        """
        Тест: Попытка получения несуществующей категории.

        Ожидаемый результат:
        - Статус ответа 404 (Not Found).
        - Сообщение: 'Категория не найдена'.
        """
        api_client.force_authenticate(user=admin)

        response = api_client.get(reverse("category-detail", kwargs={"pk": 9999}))

        assert response.status_code == 404
        assert response.data["detail"] == "Категория не найдена"
