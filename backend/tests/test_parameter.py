import pytest
from rest_framework import status
from django.urls import reverse
from backend.models import Parameter
import json


@pytest.mark.django_db
class TestParameterViewSet:
    """Набор тестов для работы с параметрами."""

    def test_list_parameters_unauthenticated(self, api_client):
        """
        Тест: Проверка, что неаутентифицированный пользователь не может получить список параметров.
        Ожидаемый результат:
        - Статус 401 Unauthorized
        """
        url = reverse("parameter-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_parameter_as_admin(self, api_client, admin, old_parameter):
        """
        Тест: Проверка, что администратор может обновить параметр.
        Ожидаемый результат:
        - Статус 200 OK
        - Имя параметра обновлено в базе данных
        """
        url = reverse("parameter-detail", args=[old_parameter.id])
        data = {"name": "New Parameter"}
        api_client.force_authenticate(user=admin)
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        old_parameter.refresh_from_db()
        assert old_parameter.name == "New Parameter"

    def test_update_parameter_as_customer(self, api_client, customer, old_parameter):
        """
        Тест: Проверка, что обычный пользователь (клиент) не может обновить параметр.
        Ожидаемый результат:
        - Статус 403 Forbidden
        """
        url = reverse("parameter-detail", args=[old_parameter.id])
        data = {"name": "New Parameter"}
        api_client.force_authenticate(user=customer)
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_parameter_as_admin(self, api_client, admin, deletable_parameter):
        """
        Тест: Проверка, что администратор может удалить параметр.
        Ожидаемый результат:
        - Статус 204 No Content
        - Параметр удален из базы данных
        """
        url = reverse("parameter-detail", args=[deletable_parameter.id])
        api_client.force_authenticate(user=admin)
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Parameter.objects.filter(id=deletable_parameter.id).exists()

    def test_create_parameter_with_existing_name(
        self, api_client, admin, old_parameter
    ):
        """
        Тест: Проверка, что нельзя создать параметр с уже существующим именем (без учета регистра).
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение о дублирующемся имени параметра
        """
        url = reverse("parameter-list")
        data = {"name": old_parameter.name.upper()}
        api_client.force_authenticate(user=admin)
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Параметр с таким именем уже существует" in response.data["name"]

    def test_create_parameter_with_empty_name(self, api_client, admin):
        """
        Тест: Проверка, что нельзя создать параметр с пустым именем.
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение о том, что имя параметра не может быть пустым
        """
        url = reverse("parameter-list")
        data = {"name": "  "}
        api_client.force_authenticate(user=admin)
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Имя параметра не может быть пустым" in response.data["name"]

    def test_create_parameter_with_non_string_name(self, api_client, admin):
        """
        Тест: Проверка, что нельзя создать параметр с именем не строкового типа.
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение о неверном типе имени
        """
        url = reverse("parameter-list")
        data = json.dumps({"name": [1, 5, "Цвет"]})

        api_client.force_authenticate(user=admin)
        response = api_client.post(url, data=data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Имя параметра должно быть строкой" in response.data["name"]

    def test_get_nonexistent_parameter_returns_error(self, api_client, admin):
        """
        Тест: Проверка, что запрос несуществующего параметра возвращает ошибку.
        Ожидаемый результат:
        - Статус 404 Not Found
        - Сообщение об ошибке "Параметр не найден"
        """
        url = reverse("parameter-detail", kwargs={"pk": 9999})
        api_client.force_authenticate(user=admin)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Параметр не найден" in response.data["detail"]

    def test_delete_parameter_as_customer(
        self, api_client, customer, deletable_parameter
    ):
        """
        Тест: Проверка, что обычный пользователь (клиент) не может удалить параметр.
        Ожидаемый результат:
        - Статус 403 Forbidden
        """
        url = reverse("parameter-detail", args=[deletable_parameter.id])
        api_client.force_authenticate(user=customer)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_parameter_str_method(self, parameter):
        """
        Тест: Проверка, что метод __str__ у параметра возвращает правильное строковое представление.
        Ожидаемый результат:
        - Строковое представление параметра равно "Test Parameter"
        """
        assert str(parameter) == "Test Parameter"
