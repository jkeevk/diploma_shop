import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Shop


@pytest.mark.django_db
class TestShopView:
    """
    Тесты для представления ShopView.
    """

    def test_create_shop_as_admin(self, api_client, admin):
        """
        Тест создания магазина пользователем с ролью admin.
        """
        api_client.force_authenticate(user=admin)

        data = {
            "name": "Admin Shop",
            "url": "http://admin.com",
        }

        url = reverse("shops")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        shop = Shop.objects.get(user=admin)
        assert shop.name == "Admin Shop"
        assert shop.url == "http://admin.com"
        assert shop.user == admin

    def test_create_shop_as_supplier(self, api_client, supplier):
        """
        Тест создания магазина пользователем с ролью supplier.
        """
        api_client.force_authenticate(user=supplier)

        data = {
            "name": "Supplier Shop",
            "url": "http://supplier.com",
        }

        url = reverse("shops")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        shop = Shop.objects.get(user=supplier)
        assert shop.name == "Supplier Shop"
        assert shop.url == "http://supplier.com"
        assert shop.user == supplier

    def test_create_shop_duplicate(self, api_client, admin):
        """
        Тест создания магазина, который уже существует.
        Должен вернуть существующий магазин.
        """
        api_client.force_authenticate(user=admin)

        existing_shop = Shop.objects.create(
            name="Existing Shop",
            url="http://existing.com",
            user=admin,
        )

        data = {
            "name": "Existing Shop",
            "url": "http://new-url.com",
        }

        url = reverse("shops")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] == existing_shop.id

    def test_create_shop_as_customer(self, api_client, customer):
        """
        Тест создания магазина пользователем с ролью customer.
        Должен вернуть ошибку, так как customer не имеет прав на создание магазина.
        """
        api_client.force_authenticate(user=customer)

        data = {
            "name": "Customer Shop",
            "url": "http://customer.com",
        }

        url = reverse("shops")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(response.data["detail"])
        