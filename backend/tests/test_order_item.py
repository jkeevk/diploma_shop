import pytest
from rest_framework.test import APIClient
from backend.models import OrderItem, Order, Product, Shop, User


@pytest.mark.django_db
class TestOrderItemModel:
    """
    Тесты для модели OrderItem.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_create_order_item(self):
        """
        Тест создания позиции заказа.
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
        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
        )
        shop = Shop.objects.create(
            name="Test Shop",
            url="http://example.com",
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            shop=shop,
            quantity=2,
        )
        assert order_item.order == order
        assert order_item.product == product
        assert order_item.shop == shop
        assert order_item.quantity == 2
