import pytest
from rest_framework import status
from django.urls import reverse
from django.core.cache import cache
import time
from django.test import override_settings


@pytest.mark.django_db
class TestThrottle:
    """Тесты для проверки механизма троттлинга в API."""

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Сбрасывает кэш перед каждым тестом."""
        from django_redis import get_redis_connection

        conn = get_redis_connection("default")
        conn.flushdb()

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_RATES": {
                "anon": "10/hour",
            }
        }
    )
    def test_anon_user_throttle(self, api_client):
        """Проверяет, что анонимный пользователь может сделать до 10 запросов,
        после чего получает статус 429 Too Many Requests.
        """
        url = reverse("category-list")
        for _ in range(10):
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            time.sleep(0.01)

        response = api_client.get(url)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_RATES": {
                "anon": "20/hour",
            }
        }
    )
    def test_authenticated_user_throttle(self, api_client, customer):
        """Проверяет, что авторизованный пользователь может сделать до 20 запросов,
        после чего получает статус 429 Too Many Requests.
        """
        url = reverse("category-list")
        api_client.force_authenticate(user=customer)
        for _ in range(20):
            response = api_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            time.sleep(0.01)

        response = api_client.get(url)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
