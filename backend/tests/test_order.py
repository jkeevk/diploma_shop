import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import OrderItem, ProductInfo
from django.core.exceptions import ValidationError
from backend.models import Order
from unittest.mock import patch
from rest_framework.exceptions import ErrorDetail


@pytest.mark.django_db
class TestBasketAPIGetRequests:
    """Тесты GET-запросов к API корзины."""

    def test_unauthenticated_user_access_to_basket(self, api_client):
        """Тест: Доступ к корзине без аутентификации.

        Ожидаемый результат:
        - Статус ответа 401 (Unauthorized).
        """
        url = reverse("basket-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_retrieves_basket(self, api_client, customer, order):
        """Тест: Получение корзины аутентифицированным пользователем.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Ответ содержит структуру корзины с элементами заказа.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert "order_items" in response.data[0]
        assert isinstance(response.data[0]["order_items"], list)

    def test_retrieve_order_with_invalid_status(self, api_client, customer, order):
        """Тест: Получение заказа с некорректным статусом.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке валидации статуса.
        """
        order.status = "invalid_status"
        order.save()
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert any("Некорректный статус" in str(error) for error in response.data)

    def test_retrieve_order_with_valid_status(self, api_client, customer, order):
        """Тест: Успешное получение заказа с допустимым статусом.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Данные ответа соответствуют ожидаемой структуре.
        """

        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", kwargs={"pk": order.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == order.id
        assert response.data["status"] == "new"


@pytest.mark.django_db
class TestBasketAPIPostRequests:
    """Тесты POST-запросов к API корзины."""

    def test_create_basket_item_with_valid_data(
        self, api_client, customer, product, shop
    ):
        """Тест: Создание элемента корзины с валидными данными.

        Ожидаемый результат:
        - Статус ответа 201 (Created).
        - Элемент корзины создан с указанным количеством.
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

    def test_create_empty_basket(self, api_client, customer, product, shop):
        """Тест: Создание пустой корзины без элементов заказа.

        Ожидаемый результат:
        - Статус ответа 201 (Created).
        - Корзина создана с пустым списком элементов.
        """
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100, price_rrc=120
        )

        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")

        data = {
            "user": customer.id,
            "order_items": [],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert [] == response.data["order_items"]

    def test_create_basket_item_missing_required_fields(
        self, api_client, customer, product, shop
    ):
        """Тест: Попытка создания элемента корзины с отсутствующими обязательными полями.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщения об ошибках для каждого отсутствующего поля.
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

    def test_create_basket_item_with_inactive_shop(
        self, api_client, supplier, customer, product, shop
    ):
        """Тест: Создание элемента корзины с неактивным магазином.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке неактивности магазина.
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
        assert "неактивен" in response.data[0]

    def test_create_basket_item_for_shop_without_owner(
        self, api_client, customer, product, shop
    ):
        """Тест: Создание элемента корзины для магазина без владельца.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке отсутствия владельца магазина.
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

    def test_create_basket_item_without_product_info(
        self, api_client, customer, product, shop
    ):
        """Тест: Создание элемента корзины без информации о продукте.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке отсутствия информации о продукте.
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

    def test_create_basket_item_exceeding_available_quantity(
        self, api_client, customer, product, shop
    ):
        """Тест: Попытка добавления товара в количестве превышающем доступное.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке недостаточного количества.
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

    def test_update_existing_item_exceeding_quantity(
        self, api_client, customer, product, shop
    ):
        """Тест: Обновление элемента корзины с превышением доступного количества.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке превышения лимита.
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
        assert "Превышение доступного количества" in str(response.data[0])

    def test_post_request_updates_existing_basket_item(
        self, api_client, customer, product, shop
    ):
        """Тест: Обновление существующего элемента корзины через POST.

        Ожидаемый результат:
        - Статус ответа 201 (Created).
        - Количество товара в элементе корзины обновлено.
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
class TestBasketAPIPutRequests:
    """Тесты PUT-запросов к API корзины."""

    def test_full_update_basket_item(self, api_client, customer, product, shop):
        """Тест: Полное обновление элемента корзины.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Количество товара полностью обновлено.
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
    def test_put_request_validation_errors(
        self, api_client, shop, customer, product, test_case
    ):
        """Тест: Обработка ошибок валидации при PUT-запросе.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщения об ошибках соответствуют тест-кейсам.
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
class TestBasketAPIPatchRequests:
    """Тесты PATCH-запросов к API корзины."""

    def test_partial_update_item_quantity(self, api_client, customer, product, shop):
        """Тест: Частичное обновление количества товара.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Количество товара успешно изменено.
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

    def test_partial_update_with_invalid_product(
        self, api_client, customer, product, shop, another_product
    ):
        """Тест: Попытка обновления несуществующего товара.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке отсутствия элемента.
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

    def test_partial_update_with_invalid_quantity(
        self, api_client, customer, product, shop
    ):
        """Тест: Обновление с недопустимым количеством товара.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке недостаточного количества.
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

    def test_partial_update_missing_shop(self, api_client, customer, product, shop):
        """Тест: Частичное обновление без указания магазина.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Остальные данные сохраняются.
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
        update_data = {"order_items": [{"product": product.id, "quantity": 5}]}

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        print(response.data)
        assert response.data["order_items"][0]["quantity"] == 5
        assert response.data["order_items"][0]["shop"] == shop.id
        assert response.data["order_items"][0]["product"] == product.id

    def test_partial_update_missing_product(self, api_client, customer, product, shop):
        """Тест: Частичное обновление без указания товара.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Остальные данные сохраняются.
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
        update_data = {"order_items": [{"shop": shop.id, "quantity": 3}]}

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        print(response.data)
        assert response.data["order_items"][0]["quantity"] == 3
        assert response.data["order_items"][0]["product"] == product.id
        assert response.data["order_items"][0]["shop"] == shop.id

    def test_partial_update_missing_shop_and_product(
        self, api_client, customer, product, shop
    ):
        """Тест: Частичное обновление без магазина и товара.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Изменяется только указанное поле.
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
        update_data = {"order_items": [{"quantity": 1}]}

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        print(response.data)
        assert response.data["order_items"][0]["quantity"] == 1
        assert response.data["order_items"][0]["product"] == product.id
        assert response.data["order_items"][0]["shop"] == shop.id

    def test_partial_update_with_empty_data(self, api_client, customer, product, shop):
        """Тест: Частичное обновление с пустыми данными.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Данные остаются без изменений.
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
        update_data = {"order_items": [{}]}

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        print(response.data)
        assert response.data["order_items"][0]["quantity"] == 2
        assert response.data["order_items"][0]["product"] == product.id
        assert response.data["order_items"][0]["shop"] == shop.id

    def test_partial_update_without_changes(self, api_client, customer, product, shop):
        """Тест: Частичное обновление без изменений данных.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Данные остаются идентичными.
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
class TestBasketAPIDeleteRequests:
    """Тесты DELETE-запросов к API корзины."""

    def test_delete_basket(self, api_client, customer, order):
        """Тест: Удаление корзины.

        Ожидаемый результат:
        - Статус ответа 204 (No Content).
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_another_users_basket(self, api_client, customer_login, order):
        """Тест: Попытка удаления чужой корзины.

        Ожидаемый результат:
        - Статус ответа 404 (Not Found).
        - Сообщение об ошибке отсутствия корзины.
        """
        api_client.force_authenticate(user=customer_login)
        url = reverse("basket-detail", args=[order.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "Корзина не найдена."


@pytest.mark.django_db
class TestBasketAdditionalFunctionality:
    """Тесты дополнительной функциональности корзины."""

    def test_order_string_representation(self, order):
        """Тест: Строковое представление заказа.

        Ожидаемый результат:
        - Строка содержит ID заказа.
        """
        assert f"Заказ номер {order.id} - " in str(order)

    def test_order_item_string_representation(self, order_item):
        """Тест: Строковое представление элемента заказа.

        Ожидаемый результат:
        - Строка содержит название товара и количество.
        """
        assert f"{order_item.product.name} : {order_item.quantity}" in str(order_item)

    def test_order_validation_with_invalid_status(self):
        """Тест: Валидация заказа с недопустимым статусом.

        Ожидаемый результат:
        - Вызывается ValidationError.
        - Сообщение об ошибке содержит невалидный статус.
        """
        order = Order(status="invalid_status")

        with pytest.raises(ValidationError) as excinfo:
            order.full_clean()

        assert "Некорректный статус" in str(excinfo.value)
        assert "invalid_status" in str(excinfo.value)

    def test_order_validation_with_valid_status(self, order):
        """Тест: Успешная валидация заказа с допустимым статусом.

        Ожидаемый результат:
        - Валидация проходит без ошибок.
        """
        order.full_clean()
        assert order.status == "new"

    def test_order_item_cost_calculation_without_price(self, shop, product, order):
        """Тест: Расчет стоимости элемента заказа без цены.

        Ожидаемый результат:
        - Возвращается нулевая стоимость.
        """
        ProductInfo.objects.filter(product=product, shop=shop).delete()
        order_item = OrderItem.objects.create(
            order=order, product=product, shop=shop, quantity=2
        )

        assert order_item.cost() == 0

    def test_order_confirmation_without_items(self, customer):
        """Тест: Подтверждение заказа без товаров.

        Ожидаемый результат:
        - Письмо поставщику не отправляется.
        """
        order = Order.objects.create(user=customer, status="new")

        with patch("backend.signals.send_email_to_host_async.delay") as mock_send_email:
            order.status = "confirmed"
            order.save()
            mock_send_email.assert_not_called()

    def test_customer_allowed_status_changes(self, api_client, product_info, customer):
        """Тест: Изменение статуса заказа покупателем.

        Ожидаемый результат:
        - Успешное изменение разрешенных статусов.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 2,
                }
            ],
            "status": "new",
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 7,
                }
            ],
            "status": "canceled",
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "canceled"
        assert response.data["order_items"][0]["quantity"] == 7

    def test_customer_forbidden_status_changes(
        self, api_client, product_info, customer
    ):
        """Тест: Попытка изменения запрещенных статусов покупателем.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке прав доступа.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 2,
                }
            ],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order_id = response.data["id"]

        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 5,
                }
            ],
            "status": "delayed",
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Недостаточно прав. Вы можете устанавливать только: new, canceled"
            in response.data[0]
        )

    def test_admin_status_changes(self, api_client, product_info, admin, customer):
        """Тест: Изменение статуса заказа администратором.

        Ожидаемый результат:
        - Успешное изменение любого статуса.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 2,
                }
            ],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order_id = response.data["id"]

        api_client.force_authenticate(user=admin)
        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 5,
                }
            ],
            "status": "assembled",
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "assembled"
        assert response.data["order_items"][0]["quantity"] == 5

    def test_supplier_status_changes(
        self, api_client, product_info, supplier, customer
    ):
        """Тест: Изменение статуса заказа поставщиком.

        Ожидаемый результат:
        - Успешное изменение любого статуса.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 2,
                }
            ],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order_id = response.data["id"]

        api_client.force_authenticate(user=supplier)
        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 2,
                }
            ],
            "status": "sent",
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "sent"
        assert response.data["order_items"][0]["quantity"] == 2

    def test_invalid_status_update(self, api_client, product_info, admin, customer):
        """Тест: Попытка установки невалидного статуса.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке валидации.
        """
        api_client.force_authenticate(user=customer)
        url = reverse("basket-list")
        data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 2,
                }
            ],
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        order_id = response.data["id"]

        api_client.force_authenticate(user=admin)
        update_url = reverse("basket-detail", args=[order_id])
        update_data = {
            "user": customer.id,
            "order_items": [
                {
                    "product": product_info.product.id,
                    "shop": product_info.shop.id,
                    "quantity": 5,
                }
            ],
            "status": "invalid",
        }

        response = api_client.patch(update_url, update_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Некорректный статус" in response.data[0]

    def test_unauthorized_status_update(self, api_client, order):
        """Тест: Попытка изменения статуса без аутентификации.

        Ожидаемый результат:
        - Статус ответа 401 (Unauthorized).
        """
        url = reverse("basket-detail", args=[order.id])
        data = {"status": "canceled"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
