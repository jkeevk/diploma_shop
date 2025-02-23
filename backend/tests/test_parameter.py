import pytest
from rest_framework.test import APIClient
from backend.models import Parameter


@pytest.mark.django_db
class TestParameterModel:
    """
    Тесты для модели Parameter.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_parameter(self):
        """
        Тест создания параметра.
        """
        parameter = Parameter.objects.create(
            name="Test Parameter",
        )
        assert parameter.name == "Test Parameter"
