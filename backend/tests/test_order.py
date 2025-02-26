import pytest
from backend.models import Order, User
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class TestOrderModel:
    """
    Тесты для модели Order.
    """

    def test_create_order(self, customer):
        """
        Тест создания заказа для клиента.
        """
        order = Order.objects.create(user=customer, status="new")
        assert order.user == customer
        assert order.status == "new"
        assert order.id is not None

    def test_create_order_as_supplier(self, supplier):
        """
        Тест создания заказа для поставщика.
        """
        order = Order.objects.create(user=supplier, status="new")
        assert order.user == supplier
        assert order.status == "new"
        assert order.id is not None

    def test_create_order_as_admin(self, admin):
        """
        Тест создания заказа для администратора.
        """
        order = Order.objects.create(user=admin, status="new")
        assert order.user == admin
        assert order.status == "new"
        assert order.id is not None

    def test_order_status_update(self, customer):
        """
        Тест обновления статуса заказа.
        """
        order = Order.objects.create(user=customer, status="new")
        order.status = "processed"
        order.save()
        updated_order = Order.objects.get(id=order.id)
        assert updated_order.status == "processed"

    def test_order_create_invalid_status(self, customer):
        """
        Тест создания заказа с некорректным статусом.
        """
        with pytest.raises(ValidationError):
            order = Order(user=customer, status="invalid_status")
            order.full_clean() 

    def test_order_assigned_to_correct_user(self, customer, admin):
        """
        Тест, чтобы заказ был привязан к правильному пользователю.
        """
        order = Order.objects.create(user=customer, status="new")
        assert order.user == customer
        assert order.user != admin

    def test_multiple_orders_for_user(self, customer):
        """
        Тест, чтобы пользователь мог иметь несколько заказов.
        """
        order1 = Order.objects.create(user=customer, status="new")
        order2 = Order.objects.create(user=customer, status="processed")
        assert order1.user == customer
        assert order2.user == customer
        assert order1.id != order2.id

    @pytest.mark.parametrize("user_role", ["supplier", "customer"])
    def test_order_creation_with_user_roles(self, user_role):
        """
        Тест, чтобы проверить создание заказа с разными ролями пользователей.
        """
        user = User.objects.create_user(
            email=f"{user_role}@example.com",
            password="password",
            first_name=f"{user_role.capitalize()}",
            last_name="User",
            role=user_role,
        )

        order = Order.objects.create(user=user, status="new")
        assert order.user == user
        assert order.status == "new"
