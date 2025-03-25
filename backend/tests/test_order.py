import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import OrderItem, ProductInfo
from django.core.exceptions import ValidationError
from backend.models import Order
from unittest.mock import patch
from rest_framework.exceptions import ErrorDetail


@pytest.mark.django_db
class TestBasketAPI_GET:
    """
    Тесты для GET запросов API корзины (/basket)
    """

    def test_get_basket_unauthenticated(self, api_client):
        """
        Неавторизованный доступ к корзине
        """
        url = reverse("basket-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

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

    def test_order_with_invalid_status(self, api_client, customer, order):
        """
        Тест получения заказа с некорректным статусом
        """
        order.status = "invalid_status"
        order.save()
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert any("Некорректный статус" in str(error) for error in response.data)

    def test_retrieve_basket_with_valid_status(self, api_client, customer, order):
        """
        Проверяем успешное получение корзины с валидным статусом (например, "new").
        """

        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", kwargs={"pk": order.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == order.id
        assert response.data["status"] == "new"


@pytest.mark.django_db
class TestBasketAPI_POST:
    """
    Тесты для POST запросов API корзины.
    """

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
                "expected_error": "Не указан магазин",
            },
            {
                "data": {
                    "order_items": [
                        {"product": product.id, "shop": shop.id, "quantity": 2}
                    ],
                },
                "expected_error": "Пользователь не указан",
            },
            {
                "data": {
                    "user": customer.id,
                    "order_items": [{"product": None, "shop": shop.id, "quantity": 2}],
                },
                "expected_error": "Не указан товар",
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

    def test_post_update_basket_item_as_customer(
        self, api_client, customer, product, shop
    ):
        """
        Обновление элемента корзины POST запросом с валидными данными
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
        order_id = response.data["id"]

        update_url = reverse("basket-list")
        update_data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 5}],
        }

        response = api_client.post(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert OrderItem.objects.first().quantity == 7


@pytest.mark.django_db
class TestBasketAPI_PUT:
    """
    Тесты для PUT запросов API корзины.
    """

    def test_put_update_basket_item_as_customer(
        self, api_client, customer, product, shop
    ):
        """
        Обновление элемента корзины с валидными данными
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")

        data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 5}],
        }

        response = api_client.post(url, data, format="json")
        print(response.data)

        assert response.status_code == status.HTTP_201_CREATED
        assert OrderItem.objects.count() == 1
        assert OrderItem.objects.first().quantity == 5
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 10}],
        }

        response = api_client.put(update_url, update_data, format="json")
        print(response.data)

        assert response.status_code == status.HTTP_200_OK
        assert OrderItem.objects.first().quantity == 10

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "missing_quantity",
                "data": {"product": "product.id", "shop": "shop.id"},
                "expected_errors": {"quantity": ["Обязательное поле не указано"]},
            },
            {
                "name": "invalid_shop_null",
                "data": {"product": "product.id", "shop": None, "quantity": 10},
                "expected_errors": {"shop": ["Не указан магазин"]},
            },
        ],
    )
    def test_update_basket_validation(
        self, api_client, shop, customer, product, test_case
    ):
        """
        Проверка валидации при обновлении корзины через PUT
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=20, price=100, price_rrc=120
        )

        order = Order.objects.create(user=customer)
        OrderItem.objects.create(order=order, product=product, shop=shop, quantity=5)

        update_data = {"order_items": [test_case["data"]]}

        for item in update_data["order_items"]:
            for key in item:
                if item[key] == "product.id":
                    item[key] = product.id
                elif item[key] == "shop.id":
                    item[key] = shop.id

        api_client.force_authenticate(user=customer)
        response = api_client.put(
            reverse("basket-detail", args=[order.id]), update_data, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        if "quantity" in test_case["expected_errors"]:
            assert "'quantity'" in response.data
            for msg in test_case["expected_errors"]["quantity"]:
                assert msg in str(response.data["'quantity'"])

        if "shop" in test_case["expected_errors"]:
            assert "order_items" in response.data
            assert isinstance(response.data["order_items"], list)
            assert len(response.data["order_items"]) > 0
            assert "shop" in response.data["order_items"][0]
            for msg in test_case["expected_errors"]["shop"]:
                assert msg in str(response.data["order_items"][0]["shop"])


@pytest.mark.django_db
class TestBasketAPI_PATCH:
    """
    Тесты для PATCH запросов API корзины.
    """

    def test_patch_update_basket_item_quantity(
        self, api_client, customer, product, shop
    ):
        """
        Частичное обновление элемента корзины (изменение только количества)
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
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 5}]
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK

        updated_order = response.data
        assert updated_order["order_items"][0]["quantity"] == 5

    def test_patch_update_basket_item_product(
        self, api_client, customer, product, shop, another_product
    ):
        """
        Проверка, что при попытке обновить товар, который не существует, возвращается ошибка с кодом 400.
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )
        ProductInfo.objects.create(
            product=another_product, shop=shop, quantity=10, price=150, price_rrc=180
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        data = {
            "user": customer.id,
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 2}],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "order_items": [
                {"product": another_product.id, "shop": shop.id, "quantity": 2}
            ]
        }

        response = api_client.patch(update_url, update_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert isinstance(response.data[0], ErrorDetail)
        assert response.data[0] == "Элемент заказа не найден для обновления"

    def test_patch_update_basket_item_invalid_quantity(
        self, api_client, customer, product, shop
    ):
        """
        Частичное обновление элемента корзины с некорректным количеством
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
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 20}]
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара" in response.content.decode("utf-8")

    def test_patch_update_basket_item_missing_shop(
        self, api_client, customer, product, shop
    ):
        """
        Частичное обновление элемента корзины без указания магазина
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
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "order_items": [{"product": product.id, "shop": None, "quantity": 5}]
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Не указан магазин" in response.content.decode("utf-8")

    def test_patch_update_basket_item_no_changes(
        self, api_client, customer, product, shop
    ):
        """
        Частичное обновление элемента корзины без изменений
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
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "order_items": [{"product": product.id, "shop": shop.id, "quantity": 2}]
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["order_items"][0]["quantity"] == 2


@pytest.mark.django_db
class TestBasketAPI_DELETE:
    """
    Тесты для DELETE запросов API корзины.
    """

    def test_clear_basket(self, api_client, customer, order):
        """
        Очистка корзины через DELETE запрос
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestCustomCheck:
    """
    Тесты вне категорий.
    """

    def test_order_str_method(self, order):
        """
        Тестирование строкового представления заказа
        """
        assert f"Заказ номер {order.id} - " in str(order)

    def test_order_item_str_method(self, order_item):
        """
        Тестирование строкового представления элемента заказа
        """
        assert f"{order_item.product.name} : {order_item.quantity}" in str(order_item)

    def test_order_clean_with_invalid_status(self):
        """Проверяет, что метод clean() вызывает ValidationError при невалидном статусе."""
        order = Order(status="invalid_status")

        with pytest.raises(ValidationError) as excinfo:
            order.full_clean()

        assert "Некорректный статус" in str(excinfo.value)
        assert "invalid_status" in str(excinfo.value)

    def test_order_clean_with_valid_status(self, order):
        """
        Проверяет, что метод clean() не вызывает ошибку при валидном статусе.
        """
        order.full_clean()
        assert order.status == "new"

    def test_order_item_cost_without_price(self, shop, product, order):
        """
        Проверяет, что cost() возвращает 0, когда нет информации о цене товара.
        """
        ProductInfo.objects.filter(product=product, shop=shop).delete()
        order_item = OrderItem.objects.create(
            order=order, product=product, shop=shop, quantity=2
        )

        assert order_item.cost() == 0

    def test_send_email_no_shops(self, customer):
        """
        Проверяем случай, когда в заказе нет товаров.
        """
        order = Order.objects.create(user=customer, status="new")

        with patch("backend.signals.send_email_to_host_async.delay") as mock_send_email:
            order.status = "confirmed"
            order.save()
            mock_send_email.assert_not_called()
