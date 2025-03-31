import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestVkAuthStatus:
    """
    Тесты для вк авторизации.
    """

    def test_status_200(self, api_client):
        """
        Тест.
        """

        url = reverse("vk-auth")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
