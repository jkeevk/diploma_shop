import pytest
from rest_framework import status
from django.urls import reverse
from django.core.cache import cache


@pytest.mark.throttling
@pytest.mark.django_db
class TestThrottle:
    """Тесты для проверки механизма троттлинга в API."""

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Сбрасывает кэш перед каждым тестом."""
        cache.clear()
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def test_anon_user_throttle(self, api_client):
        """Проверяет, что анонимный пользователь может сделать до 300 запросов,
        после чего получает статус 429 Too Many Requests.
        """
        url = reverse("category-list")
        for _ in range(300):
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK

        response = api_client.get(url)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_authenticated_user_throttle(self, api_client, customer):
        """Проверяет, что авторизованный пользователь может сделать до 500 запросов,
        после чего получает статус 429 Too Many Requests.
        """
        url = reverse("category-list")
        api_client.force_authenticate(user=customer)
        for _ in range(500):
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK

        response = api_client.get(url)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
