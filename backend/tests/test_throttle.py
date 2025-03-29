import pytest
from rest_framework import status
from django.urls import reverse
from django.test import override_settings


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
@pytest.mark.django_db
def test_anon_user_throttle(api_client):
    """Проверяет, что анонимный пользователь может сделать до 100 запросов,
    после чего получает статус 429 Too Many Requests.
    """
    url = reverse("category-list")
    for _ in range(100):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    response = api_client.get(url)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
@pytest.mark.django_db
def test_authenticated_user_throttle(api_client, customer):
    """Проверяет, что авторизованный пользователь может сделать до 200 запросов,
    после чего получает статус 429 Too Many Requests.
    """
    url = reverse("category-list")
    api_client.force_authenticate(user=customer)
    for _ in range(200):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    response = api_client.get(url)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
