import pytest
from rest_framework.test import APIClient
from backend.models import Order, User


@pytest.mark.django_db
class TestOrderModel:
    """
    Тесты для модели Order.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_order(self):
        """
        Тест создания заказа.
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            first_name="Test",
            last_name="User",
            role="customer",
        )
        order = Order.objects.create(
            user=user,
            status="new",
        )
        assert order.user == user
        assert order.status == "new"
        