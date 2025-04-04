import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import User, Order, OrderItem
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestUserOrdersView:
    """
    Тесты для получения списка заказов покупателя.
    """

    def test_get_orders_authenticated(
        self, contact, api_client, customer, order, product, shop
    ):
        """Тест получения заказов для авторизованного пользователя."""
        api_client.force_authenticate(user=customer)
        order = Order.objects.create(user=customer)
        order_item = OrderItem.objects.create(
            order=order, product=product, shop=shop, quantity=2
        )
        url = reverse("confirm-basket", args=[contact.id])

        response = api_client.post(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "Заказ успешно подтвержден."}
        response = api_client.get(reverse("user-orders"))

        order.refresh_from_db()
        assert order.status == "confirmed"
        assert order_item.product.name == "Test Product"
        assert order_item.product.category.name == "Test Category"
        assert order_item.quantity == 2

        assert response.status_code == status.HTTP_200_OK

        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert response.data[0]["id"] == order.id

    def test_get_orders_anonymous(self, api_client):
        """Тест получения заказов для анонимного пользователя."""
        response = api_client.get(reverse("user-orders"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"
        assert "Пожалуйста, войдите в систему." == response.data["detail"]


@pytest.mark.django_db
class TestUserManager:

    User = get_user_model()

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_manager = User.objects

    def test_create_user_with_email(self):
        """Тест создания пользователя с email."""
        user = self.user_manager.create_user(
            email="test@example.com", password="password123"
        )
        assert user.email == "test@example.com"
        assert user.check_password("password123")
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_without_email(self):
        """Тест создания пользователя без email."""
        with pytest.raises(ValueError, match="Поле Email должно быть заполнено"):
            self.user_manager.create_user(email="", password="password123")

    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        superuser = self.user_manager.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        assert superuser.email == "admin@example.com"
        assert superuser.check_password("adminpass")
        assert superuser.is_staff
        assert superuser.is_superuser

    def test_create_superuser_without_is_staff(self):
        """Тест создания суперпользователя без is_staff."""
        with pytest.raises(
            ValueError, match="Суперпользователь должен иметь is_staff=True."
        ):
            self.user_manager.create_superuser(
                email="admin@example.com", password="adminpass", is_staff=False
            )

    def test_create_superuser_without_is_superuser(self):
        """Тест создания суперпользователя без is_superuser."""
        with pytest.raises(
            ValueError, match="Суперпользователь должен иметь is_superuser=True."
        ):
            self.user_manager.create_superuser(
                email="admin@example.com", password="adminpass", is_superuser=False
            )

    def test_user_str_method(self, customer_login):
        """Тест строкового представления пользователя."""
        assert str(customer_login) == "customer@example.com"
