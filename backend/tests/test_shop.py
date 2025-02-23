import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import Shop, User


@pytest.mark.django_db
class TestShopView:
    """
    Тесты для представления ShopView.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_shop_as_admin(self):
        """
        Тест создания магазина пользователем с ролью admin.
        """
        user = User.objects.create_user(
            email="admin@example.com",
            password="strongpassword123",
            first_name="Admin",
            last_name="User",
            role="admin",
        )
        self.client.force_authenticate(user=user)

        data = {
            "name": "Admin Shop",
            "url": "http://admin.com",
        }

        url = reverse("shops")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        shop = Shop.objects.get(user=user)
        assert shop.name == "Admin Shop"
        assert shop.url == "http://admin.com"
        assert shop.user == user

    def test_create_shop_as_supplier(self):
        """
        Тест создания магазина пользователем с ролью supplier.
        """
        user = User.objects.create_user(
            email="supplier@example.com",
            password="strongpassword123",
            first_name="Supplier",
            last_name="User",
            role="supplier",
        )
        self.client.force_authenticate(user=user)

        data = {
            "name": "Supplier Shop",
            "url": "http://supplier.com",
        }

        url = reverse("shops")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        shop = Shop.objects.get(user=user)
        assert shop.name == "Supplier Shop"
        assert shop.url == "http://supplier.com"
        assert shop.user == user

    def test_create_shop_duplicate(self):
        """
        Тест создания магазина, который уже существует.
        Должен вернуть существующий магазин.
        """
        user = User.objects.create_user(
            email="admin@example.com",
            password="strongpassword123",
            first_name="Admin",
            last_name="User",
            role="admin",
        )
        self.client.force_authenticate(user=user)

        existing_shop = Shop.objects.create(
            name="Existing Shop",
            url="http://existing.com",
            user=user,
        )

        data = {
            "name": "Existing Shop",
            "url": "http://new-url.com",
        }

        url = reverse("shops")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] == existing_shop.id

    def test_create_shop_as_customer(self):
        """
        Тест создания магазина пользователем с ролью customer.
        Должен вернуть ошибку, так как customer не имеет прав на создание магазина.
        """
        user = User.objects.create_user(
            email="customer@example.com",
            password="strongpassword123",
            first_name="Customer",
            last_name="User",
            role="customer",
        )
        self.client.force_authenticate(user=user)

        data = {
            "name": "Customer Shop",
            "url": "http://customer.com",
        }

        url = reverse("shops")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "У вас недостаточно прав для выполнения этого действия." in str(response.data["detail"])
        