import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Order, OrderItem
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestPartnerOrders:
    def test_get_orders_success(self, api_client, supplier, customer, shop, product):
        """
        Тест успешного получения заказов.
        """
        api_client.force_authenticate(user=supplier)
        order = Order.objects.create(user=customer, status="confirmed")
        OrderItem.objects.create(order=order, product=product, shop=shop, quantity=2)

        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_orders_no_shop(self, api_client, supplier):
        """
        Тест получения заказов без привязанного магазина.
        """
        api_client.force_authenticate(user=supplier)
        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Вы не связаны с магазином."

    def test_get_orders_anonymous_user(self, api_client):
        """
        Тест получения заказов анонимным пользователем.
        """
        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "Вы не авторизованы. Пожалуйста, войдите в систему."
        )

    def test_get_orders_as_non_supplier(self, api_client, customer):
        """
        Тест получения заказов пользователем без роли 'supplier'.
        """
        api_client.force_authenticate(user=customer)

        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "У вас недостаточно прав для выполнения этого действия."
        )

    def test_order_total_cost(self, order):
        """
        Тест расчета общей стоимости заказа.
        """
        assert order.total_cost() == 200

    def test_order_total_cost_if_order_has_no_items(self, order, product, shop):
        """
        Тест расчета общей стоимости заказа если у заказа нет товаров.
        """
        order_item = OrderItem.objects.create(order=order,
                                                product=product, 
                                                shop=shop, 
                                                quantity=0
                                                )
        assert order_item.cost() == 0


    def test_order_clean_invalid_status(self, order, supplier):
        """
        Тест проверки статуса заказа на валидность.
        """
        order = Order(user=supplier, status="invalid_status")
        with pytest.raises(ValidationError) as excinfo:
            order.clean()
        assert "Некорректный статус" in str(excinfo.value)
