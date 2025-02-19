import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """Фикстура для создания тестового клиента API.

    Возвращает экземпляр APIClient, который можно использовать для
    выполнения запросов к API в тестах.
    """
    return APIClient()