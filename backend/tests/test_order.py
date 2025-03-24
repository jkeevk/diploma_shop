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
        assert "order_items" in response.data[0]
        assert isinstance(response.data[0]["order_items"], list)

    def test_create_basket_item_as_customer(self, api_client, customer, product, shop):
        """
        Создание элемента корзины с валидными данными
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")

        data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 2}],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert OrderItem.objects.count() == 1
        assert OrderItem.objects.first().quantity == 2

    def test_create_basket_item_as_customer_empty_fields(
        self, api_client, customer, product, shop
    ):
        """
        Создание элемента корзины c незаполненными полями
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")

        test_cases = [
            {
                "data": {
                    "user": customer.id,
                    "order_items": [
                        {"product": product.id, "shop": None, "quantity": 2}
                    ],
                },
                "expected_error": "This field may not be null.",
            },
            {
                "data": {
                    "user": None,
                    "order_items": [
                        {"product": product.id, "shop": shop.id, "quantity": 2}
                    ],
                },
                "expected_error": "This field may not be null.",
            },
            {
                "data": {
                    "user": customer.id,
                    "order_items": [{"product": None, "shop": shop.id, "quantity": 2}],
                },
                "expected_error": "This field may not be null.",
            },
        ]

        for case in test_cases:
            response = api_client.post(url, case["data"], format="json")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert case["expected_error"] in response.content.decode("utf-8")

    def test_create_basket_item_as_customer_shop_inactive(
        self, api_client, supplier, customer, product, shop
    ):
        """
        Создание элемента корзины с отключенным магазином
        """
        supplier.is_active = False
        supplier.save()

        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")

        data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 2}],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Невозможно создать заказ." in response.data[0]

    def test_create_basket_item_shop_without_owner(
        self, api_client, customer, product, shop
    ):
        """
        Создание элемента корзины из магазина к которому не привязан поставщик
        """
        shop.user = None
        shop.save()

        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")

        data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 2}],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "не привязан к пользователю" in response.data[0]

    def test_create_basket_item_no_product_info(
        self, api_client, customer, product, shop
    ):
        """
        Создание элемента корзины без информации о продукте
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")

        data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 2}],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "отсутствует в магазине" in response.data[0]

    def test_add_to_basket_invalid_quantity(self, api_client, customer, product, shop):
        """
        Попытка добавить товар в количестве, превышающем доступное
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=5, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        response = api_client.post(
            reverse("basket-list"),
            {
                "user": customer.id,
                "order_items": [
                    {"product": product.id, "shop": shop.id, "quantity": 10}
                ],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара" in response.content.decode("utf-8")

    def test_create_order_with_existing_item_exceeding_quantity(
        self, api_client, customer, product, shop
    ):
        """
        Тест на создание заказа с обновлением существующего элемента и превышением количества.
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)

        api_client.post(
            reverse("basket-list"),
            {
                "user": customer.id,
                "order_items": [
                    {"product": product.id, "shop": shop.id, "quantity": 5}
                ],
            },
            format="json",
        )

        response = api_client.post(
            reverse("basket-list"),
            {
                "user": customer.id,
                "order_items": [
                    {"product": product.id, "shop": shop.id, "quantity": 6}
                ],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Добавление товара" in str(response.data[0])

    def test_clear_basket(self, api_client, customer, order):
        """
        Очистка корзины через DELETE запрос
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_order_with_invalid_status(self, api_client, customer, order):
        """
        Тестирование заказа с некорректным статусом
        """
        order.status = "invalid_status"
        order.save()
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert any("Некорректный статус" in str(error) for error in response.data)

    def test_order_str_method(self, order):
        """
        Тестирование строкового представления заказа
        """
        assert f"Заказ номер {order.id} - " in str(order)

    def test_order_item_str_method(self, order_item):
        """
        Тестирование строкового представления элемента заказа
        """
        assert f"{order_item.product.name} : {order_item.quantity}" in str(
            order_item
        )

