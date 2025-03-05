import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import OrderItem, ProductInfo

@pytest.mark.django_db
class TestBasketAPI:
    """
    Тесты для API корзины (/basket)
    """

    def test_get_basket_unauthenticated(self, api_client):
        """
        Неавторизованный доступ к корзине
        """
        url = reverse("basket-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_basket_authenticated(self, api_client, customer, order):
        """
        Получение корзины для авторизованного пользователя
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert 'order_items' in response.data[0]
        assert isinstance(response.data[0]['order_items'], list) 

    def test_create_basket_item_as_customer(self, api_client, customer, product, shop):
        """Создание элемента корзины с валидными данными"""
        ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100,
            price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        
        data = {
            "user": customer.id,
            "order_items": [{
                "product": product.id,
                "shop": shop.id,
                "quantity": 2
            }]
        }
        
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert OrderItem.objects.count() == 1
        assert OrderItem.objects.first().quantity == 2

    def test_add_to_basket_invalid_quantity(self, api_client, customer, product, shop):
        """
        Попытка добавить товар в количестве, превышающем доступное
        """
        ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=5,
            price=100,
            price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        response = api_client.post(reverse("basket-list"), {
            "user": customer.id,
            "order_items": [{
                "product": product.id,
                "shop": shop.id,
                "quantity": 10
            }]
        }, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара" in response.content.decode('utf-8')

    def test_update_basket_item_quantity(self, api_client, customer, order_item):
        """
        Обновление количества товара в корзине
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order_item.id])
        
        new_data = {
            "order_items": [{
                "product": order_item.product.id,
                "shop": order_item.shop.id,
                "quantity": 5
            }]
        }
        
        response = api_client.patch(url, new_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        order_item.refresh_from_db()
        assert order_item.quantity == 5

    def test_clear_basket(self, api_client, customer, order):
        """
        Очистка корзины через DELETE запрос
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
