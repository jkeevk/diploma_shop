from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import pytest

from backend.models import Parameter

@pytest.mark.django_db
class TestParameterViewSet:
    """
    Тесты для вьюсета параметров.
    """
    def test_list_parameters_unauthenticated(self, api_client):
        """
        Тест получения списка параметров неавторизованным пользователем.
        """
        url = reverse("parameter-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_parameter_as_admin(self, api_client, admin):
        """
        Тест обновления параметра администратором.
        """
        parameter = Parameter.objects.create(name="Old Parameter")
        url = reverse("parameter-detail", args=[parameter.id])
        data = {"name": "New Parameter"}
        api_client.force_authenticate(user=admin)
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        parameter.refresh_from_db()
        assert parameter.name == "New Parameter"

    def test_update_parameter_as_customer(self, api_client, customer):
        """
        Тест обновления параметра пользователем с ролью customer.
        Должен вернуть ошибку 403.
        """
        parameter = Parameter.objects.create(name="Old Parameter")
        url = reverse("parameter-detail", args=[parameter.id])
        data = {"name": "New Parameter"}
        api_client.force_authenticate(user=customer)
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_parameter_as_admin(self, api_client, admin):
        """
        Тест удаления параметра администратором.
        """
        parameter = Parameter.objects.create(name="Parameter to delete")
        url = reverse("parameter-detail", args=[parameter.id])
        api_client.force_authenticate(user=admin)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Parameter.objects.filter(id=parameter.id).exists()

    def test_delete_parameter_as_customer(self, api_client, customer):
        """
        Тест удаления параметра пользователем с ролью customer.
        Должен вернуть ошибку 403.
        """
        parameter = Parameter.objects.create(name="Parameter to delete")
        url = reverse("parameter-detail", args=[parameter.id])
        api_client.force_authenticate(user=customer)
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_parameter_str_method(self):
        """
        Тест метода __str__ модели Parameter.
        """
        parameter = Parameter.objects.create(name="Test Parameter")
        assert str(parameter) == "Test Parameter"
        