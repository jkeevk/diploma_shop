import pytest
from rest_framework import status
from django.urls import reverse
from backend.models import Parameter
from backend.serializers import ProductInfoSerializer

@pytest.mark.django_db
class TestParameterViewSet:
    """
    Тесты для представления параметров.
    """

    def test_list_parameters_unauthenticated(self, api_client):
        """
        Проверяет, что неаутентифицированный пользователь не может получить список параметров.
        Ожидается статус 403 Forbidden.
        """
        url = reverse("parameter-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

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

    def test_delete_parameter_as_customer(self, api_client, customer, deletable_parameter):
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
