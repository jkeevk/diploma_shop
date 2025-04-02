import pytest
from rest_framework import status
from django.urls import reverse
from backend.models import Parameter
from backend.serializers import ProductInfoSerializer
import json


@pytest.mark.django_db
class TestParameterViewSet:
    """
    Тесты для представления параметров.
    """

    def test_list_parameters_unauthenticated(self, api_client):
        """
        Проверяет, что неаутентифицированный пользователь не может получить список параметров.
        Ожидается статус 401 Forbidden.
        """
        url = reverse("parameter-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_product_info_serialization(self, product_info):
        """
        Проверяет корректную сериализацию объекта ProductInfo.
        Убедитесь, что сериализованные данные содержат все необходимые поля.
        """
        serializer = ProductInfoSerializer(product_info)
        data = serializer.data

        assert "shop" in data
        assert "quantity" in data
        assert "price" in data
        assert "price_rrc" in data
        assert "parameters" in data

        expected_parameters = {
            param.parameter.name: param.value
            for param in product_info.product_parameters.all()
        }
        assert data["parameters"] == expected_parameters

    def test_update_parameter_as_admin(self, api_client, admin, old_parameter):
        """
        Проверяет, что администратор может обновить параметр.
        Ожидается статус 200 OK и обновление имени параметра в базе данных.
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
        Проверяет, что обычный пользователь (клиент) не может обновить параметр.
        Ожидается статус 403 Forbidden.
        """
        url = reverse("parameter-detail", args=[old_parameter.id])
        data = {"name": "New Parameter"}
        api_client.force_authenticate(user=customer)
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_parameter_as_admin(self, api_client, admin, deletable_parameter):
        """
        Проверяет, что администратор может удалить параметр.
        Ожидается статус 204 No Content и отсутствие параметра в базе данных.
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
        Проверяет, что нельзя создать параметр с уже существующим именем (без учета регистра).
        Ожидается статус 400 Bad Request и сообщение об ошибке.
        """
        url = reverse("parameter-list")
        data = {"name": old_parameter.name.upper()}
        api_client.force_authenticate(user=admin)
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Параметр с таким именем уже существует" in response.data["name"]

    def test_create_parameter_with_empty_name(self, api_client, admin):
        """
        Проверяет, что нельзя создать параметр с пустым именем.
        Для дополнительной проверки сериализатора заполним пробелами.
        Ожидается статус 400 Bad Request и сообщение об ошибке.
        """
        url = reverse("parameter-list")
        data = {"name": "  "}
        api_client.force_authenticate(user=admin)
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Имя параметра не может быть пустым" in response.data["name"]

    def test_create_parameter_with_non_string_name(self, api_client, admin):
        """
        Проверяет, что нельзя создать параметр с именем не строкового типа.
        Ожидается статус 400 Bad Request и сообщение об ошибке.
        """
        url = reverse("parameter-list")
        data = json.dumps({"name": [1, 5, "Цвет"]})

        api_client.force_authenticate(user=admin)
        response = api_client.post(url, data=data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Имя параметра должно быть строкой" in response.data["name"]

    def test_get_nonexistent_parameter_returns_error(self, api_client, admin):
        """
        Проверяет, что при запросе несуществующего параметра
        возвращается сообщение об ошибке.
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
        Проверяет, что обычный пользователь (клиент) не может удалить параметр.
        Ожидается статус 403 Forbidden.
        """
        url = reverse("parameter-detail", args=[deletable_parameter.id])
        api_client.force_authenticate(user=customer)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_parameter_str_method(self, parameter):
        """
        Проверяет, что метод __str__ у параметра возвращает ожидаемую строку.
        Ожидается, что строковое представление параметра равно "Test Parameter".
        """
        assert str(parameter) == "Test Parameter"
