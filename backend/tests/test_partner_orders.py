import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Order, OrderItem
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestPartnerOrders:
    """Набор тестов для работы с заказами партнера."""

    def test_supplier_can_get_orders_successfully(
        self, api_client, supplier, customer, shop, product
    ):
        """
        Тест: Успешное получение заказов.
        Ожидаемый результат:
        - Статус 200 OK
        - Количество заказов равно 1
        """
        api_client.force_authenticate(user=supplier)
        order = Order.objects.create(user=customer, status="confirmed")
        OrderItem.objects.create(order=order, product=product, shop=shop, quantity=2)

        response = api_client.get(reverse("partner-orders"))

        # Проверки
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_orders_fails_without_shop(self, api_client, supplier):
        """
        Тест: Получение заказов без привязанного магазина.
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение о том, что пользователь не связан с магазином.
        """
        api_client.force_authenticate(user=supplier)

        response = api_client.get(reverse("partner-orders"))

        # Проверки
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Вы не связаны с магазином."

    def test_anonymous_user_cannot_get_orders(self, api_client):
        """
        Тест: Получение заказов анонимным пользователем.
        Ожидаемый результат:
        - Статус 401 Unauthorized
        - Сообщение о необходимости входа в систему.
        """
        response = api_client.get(reverse("partner-orders"))

        # Проверки
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Пожалуйста, войдите в систему."

    def test_non_supplier_user_cannot_get_orders(self, api_client, customer):
        """
        Тест: Получение заказов пользователем без роли 'supplier'.
        Ожидаемый результат:
        - Статус 403 Forbidden
        - Сообщение о недостаточности прав.
        """
        api_client.force_authenticate(user=customer)

        response = api_client.get(reverse("partner-orders"))

        # Проверки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "У вас недостаточно прав для выполнения этого действия."
        )

    def test_order_total_cost_calculation(self, order):
        """
        Тест: Расчет общей стоимости заказа.
        Ожидаемый результат:
         - Общая стоимость заказа равна 200.
        """
        assert order.total_cost() == 200

    def test_order_total_cost_when_no_items(self, order, product, shop):
        """
        Тест: Расчет общей стоимости заказа если у заказа нет товаров.
        Ожидаемый результат:
        - Общая стоимость равна 0.
        """
        order_item = OrderItem.objects.create(
            order=order, product=product, shop=shop, quantity=0
        )
        assert order_item.cost() == 0

    def test_order_status_validation_on_invalid_status(self, supplier):
        """
        Тест: Проверка статуса заказа на валидность.
        Ожидаемый результат:
        - Генерация исключения ValidationError с сообщением о некорректном статусе.
        """
        order = Order(user=supplier, status="invalid_status")

        with pytest.raises(ValidationError) as excinfo:
            order.clean()

        assert "Некорректный статус" in str(excinfo.value)
