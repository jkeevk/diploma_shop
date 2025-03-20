import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Order, OrderItem, ProductInfo, User
from backend.serializers import OrderSerializer
from django.core.exceptions import ValidationError


class TestPartnerOrders:
    @pytest.mark.django_db
    def test_get_orders_success(self, api_client, supplier, customer, shop, product):
        """Тест успешного получения заказов."""
        api_client.force_authenticate(user=supplier)
        order = Order.objects.create(user=customer, status="confirmed")
        OrderItem.objects.create(order=order, product=product, shop=shop, quantity=2)

        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    @pytest.mark.django_db
    def test_get_orders_no_shop(self, api_client, supplier):
        """Тест получения заказов без привязанного магазина."""
        api_client.force_authenticate(user=supplier)
        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Вы не связаны с магазином."

    @pytest.mark.django_db
    def test_get_orders_anonymous_user(self, api_client):
        """Тест получения заказов анонимным пользователем."""
        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "Вы не авторизованы. Пожалуйста, войдите в систему."
        )

    @pytest.mark.django_db
    def test_get_orders_as_non_supplier(self, api_client, customer):
        """Тест получения заказов пользователем без роли 'supplier'."""
        api_client.force_authenticate(user=customer)

        response = api_client.get(reverse("partner-orders"))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "У вас недостаточно прав для выполнения этого действия."
        )

    @pytest.mark.django_db
    def test_order_total_cost(self, order):
        """Тест расчета общей стоимости заказа."""
        assert order.total_cost() == 200

    @pytest.mark.django_db
    def test_order_clean_invalid_status(self):
        """Тест проверки статуса заказа на валидность."""
        order = Order(user=User.objects.first(), status="invalid_status")
        with pytest.raises(ValidationError):
            order.clean()
