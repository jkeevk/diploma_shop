import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Product, Category, Shop, ProductInfo, Parameter
from backend.serializers import ProductSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError


@pytest.mark.django_db
class TestProductAPI:
    def test_retrieve_product_details(self, api_client, supplier, shop):
        """Тест: Получение деталей продукта.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Данные продукта содержат корректную информацию.
        """
        api_client.force_authenticate(user=supplier)

        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=category,
        )

        ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        url = reverse("product-detail", kwargs={"pk": product.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Product"
        assert response.data["model"] == "Test Model"
        assert response.data["category"] == "Test Category"
        assert len(response.data["product_infos"]) == 1
        assert response.data["product_infos"][0]["shop"] == shop.id
        assert response.data["product_infos"][0]["quantity"] == 10

    def test_create_product_with_associated_product_infos(
        self, api_client, supplier, shop
    ):
        """Тест: Создание продукта с привязанными информационными блоками.

        Ожидаемый результат:
        - Статус ответа 201 (Created).
        - Созданный продукт содержит переданные данные.
        """
        api_client.force_authenticate(user=supplier)
        product_data = {
            "name": "Test Product",
            "model": "Test Model",
            "category": "New_Category",
            "product_infos": [
                {
                    "shop": shop.id,
                    "quantity": 10,
                    "price": 100.00,
                    "price_rrc": 120.00,
                }
            ],
        }

        url = reverse("product-list")
        response = api_client.post(url, product_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Product"
        assert response.data["model"] == "Test Model"
        assert response.data["category"] == "New_Category"
        assert len(response.data["product_infos"]) == 1
        assert response.data["product_infos"][0]["shop"] == shop.id
        assert response.data["product_infos"][0]["quantity"] == 10

    def test_create_product_with_all_fields_including_parameters(
        self, api_client, supplier, shop
    ):
        """Тест: Создание продукта с полным набором полей и параметрами.

        Ожидаемый результат:
        - Статус ответа 201 (Created).
        """
        api_client.force_authenticate(user=supplier)
        product_data = {
            "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
            "model": "Updated Model",
            "category": "Телефоны",
            "product_infos": [
                {
                    "shop": shop.id,
                    "description": "Познакомьтесь с iPhone XS 512 ГБ в золотом цвете в Apple Store — элегантный дизайн, высокая производительность и потрясающий Super Retina дисплей. Премиум-смартфон для тех, кто ценит лучшее!",
                    "external_id": 142342,
                    "quantity": 14,
                    "price": "110000.00",
                    "price_rrc": "116990.00",
                    "parameters": {
                        "Встроенная память (Гб)": "512",
                        "Диагональ (дюйм)": "6.5",
                        "Разрешение (пикс)": "2688x1242",
                        "Цвет": "золотистый",
                    },
                }
            ],
        }

        url = reverse("product-list")
        response = api_client.post(url, product_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_update_product_with_different_shop(self, api_client, supplier, shop):
        """Тест: Обновление продукта с указанием магазина не связанного с продуктом.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщение об ошибке 'Товар не связан с магазином'.
        """
        api_client.force_authenticate(user=supplier)
        category = Category.objects.create(name="Test Category")
        new_shop = Shop.objects.create(name="New Shop")

        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=category,
        )

        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        update_data = {
            "product_infos": [
                {
                    "shop": new_shop.id,
                    "quantity": 20,
                    "price": 200.00,
                    "price_rrc": 220.00,
                }
            ]
        }

        url = reverse("product-detail", kwargs={"pk": product.id})
        response = api_client.patch(url, update_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["shop"] == "Товар не связан с магазином"

    def test_filter_products_by_shop_id(
        self, api_client, product, supplier, shop, category
    ):
        """Тест: Фильтрация продуктов по ID магазина.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Возвращаются только продукты из указанного магазина.
        """
        api_client.force_authenticate(user=supplier)
        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )
        product.product_infos.add(product_info)
        Product.objects.create(name="Product 2", category=category)

        url = reverse("product-list")
        response = api_client.get(url, {"shop": shop.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Product"
        assert response.data[0]["model"] == "Test Model"
        assert response.data[0]["category"] == "Test Category"
        assert len(response.data[0]["product_infos"]) == 1
        assert response.data[0]["product_infos"][0]["shop"] == shop.id

    def test_create_product_missing_required_fields(self, api_client, supplier):
        """Тест: Попытка создания продукта без обязательных полей.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщения об ошибках для отсутствующих полей.
        """
        api_client.force_authenticate(user=supplier)

        product_data = {
            "product_infos": [
                {
                    "shop": None,
                    "quantity": 10,
                    "price": 100.00,
                    "price_rrc": 120.00,
                }
            ],
        }

        url = reverse("product-list")
        response = api_client.post(url, product_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_update_nonexistent_product_returns_404(self, api_client, supplier):
        """Тест: Обновление несуществующего продукта.

        Ожидаемый результат:
        - Статус ответа 404 (Not Found).
        """
        api_client.force_authenticate(user=supplier)

        update_data = {
            "product_infos": [
                {
                    "shop": 100,
                    "quantity": 20,
                    "price": 200.00,
                    "price_rrc": 220.00,
                }
            ],
        }

        url = reverse("product-detail", kwargs={"pk": 999})
        response = api_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_product_with_all_fields(self, api_client, supplier, shop):
        """Тест: Частичное обновление продукта с изменением всех полей.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        """
        api_client.force_authenticate(user=supplier)
        category = Category.objects.create(name="Test Category")
        new_shop = Shop.objects.create(name="New Shop")

        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=category,
        )

        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        update_data = {
            "name": "Смартфон Apple iPhone XS Max 512GB (золотистый)",
            "model": "Updated Model",
            "category": "Телефоны",
            "product_infos": [
                {
                    "quantity": 14,
                    "price": "110000.00",
                    "price_rrc": "116990.00",
                    "parameters": {
                        "Встроенная память (Гб)": "512",
                        "Диагональ (дюйм)": "6.5",
                        "Разрешение (пикс)": "2688x1242",
                        "Цвет": "золотистый",
                    },
                }
            ],
        }

        url = reverse("product-detail", kwargs={"pk": product.id})
        response = api_client.patch(url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_create_product_with_negative_price_and_quantity(
        self, api_client, supplier, shop
    ):
        """Тест: Создание продукта с отрицательными значениями цены и количества.

        Ожидаемый результат:
        - Статус ответа 400 (Bad Request).
        - Сообщения об ошибках валидации.
        """
        api_client.force_authenticate(user=supplier)
        product_data = {
            "name": "Test Product",
            "model": "Test Model",
            "category": "New_Category",
            "product_infos": [
                {
                    "shop": shop.id,
                    "quantity": -10,
                    "price": -50.00,
                    "price_rrc": -120.00,
                }
            ],
        }

        url = reverse("product-list")
        response = api_client.post(url, product_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Цена должна быть больше 0." == str(
            response.data["product_infos"][0]["price"][0]
        )
        assert "Цена должна быть больше 0." == str(
            response.data["product_infos"][0]["price_rrc"][0]
        )
        assert "Количество не может быть отрицательным." == str(
            response.data["product_infos"][0]["quantity"][0]
        )

    def test_delete_existing_product(self, api_client, supplier, shop):
        """Тест: Удаление существующего продукта.

        Ожидаемый результат:
        - Статус ответа 204 (No Content).
        - Продукт удален из базы данных.
        """
        api_client.force_authenticate(user=supplier)

        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=category,
        )

        ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        url = reverse("product-detail", kwargs={"pk": product.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.filter(id=product.id).count() == 0

    def test_retrieve_nonexistent_product_returns_404(self, api_client, supplier):
        """Тест: Получение несуществующего продукта.

        Ожидаемый результат:
        - Статус ответа 404 (Not Found).
        """
        api_client.force_authenticate(user=supplier)

        url = reverse("product-detail", kwargs={"pk": 999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_products_without_shop_returns_all(self, api_client, supplier, shop):
        """Тест: Фильтрация продуктов без указания магазина.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Возвращаются все доступные продукты.
        """
        api_client.force_authenticate(user=supplier)

        category = Category.objects.create(name="Test Category")
        shop2 = Shop.objects.create(name="Shop 2")

        product1 = Product.objects.create(
            name="Product 1",
            model="Model 1",
            category=category,
        )
        product2 = Product.objects.create(
            name="Product 2",
            model="Model 2",
            category=category,
        )

        ProductInfo.objects.create(
            product=product1, shop=shop, quantity=10, price=100, price_rrc=110
        )
        ProductInfo.objects.create(
            product=product2, shop=shop2, quantity=5, price=200, price_rrc=110
        )
        url = reverse("product-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_products_by_nonexistent_shop_returns_empty(
        self, api_client, supplier
    ):
        """Тест: Фильтрация по несуществующему магазину.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Возвращается пустой список продуктов.
        """
        api_client.force_authenticate(user=supplier)

        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(name="Test Product", category=category)
        shop = Shop.objects.create(name="Existing Shop")
        ProductInfo.objects.create(
            product=product, shop=shop, quantity=10, price=100.00, price_rrc=120.00
        )

        url = reverse("product-list")
        response = api_client.get(url, {"shop": 999})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_filter_products_by_category_id(self, api_client, supplier):
        """Тест: Фильтрация продуктов по ID категории.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Возвращаются только продукты из указанной категории.
        """
        api_client.force_authenticate(user=supplier)

        category1 = Category.objects.create(name="Category 1")
        category2 = Category.objects.create(name="Category 2")

        product1 = Product.objects.create(name="Product 1", category=category1)
        product2 = Product.objects.create(name="Product 2", category=category2)

        shop = Shop.objects.create(name="Test Shop")
        ProductInfo.objects.create(
            product=product1, shop=shop, quantity=10, price=100, price_rrc=110
        )
        ProductInfo.objects.create(
            product=product2, shop=shop, quantity=5, price=200, price_rrc=210
        )

        url = reverse("product-list")
        response = api_client.get(url, {"category": category1.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Product 1"

    def test_filter_products_by_existing_shop_id(self, api_client, supplier):
        """Тест: Фильтрация по существующему ID магазина.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Возвращаются только продукты из указанного магазина.
        """
        api_client.force_authenticate(user=supplier)

        shop = Shop.objects.create(name="Test Shop")
        category = Category.objects.create(name="Test Category")

        product_with_shop = Product.objects.create(
            name="Product with Shop", category=category
        )
        ProductInfo.objects.create(
            product=product_with_shop,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        Product.objects.create(name="Product without Shop", category=category)

        url = reverse("product-list")
        response = api_client.get(url, {"shop": shop.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_products_with_empty_shop_param_returns_all(
        self, api_client, supplier, shop
    ):
        """Тест: Фильтрация с пустым параметром shop.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Возвращаются все доступные продукты.
        """
        api_client.force_authenticate(user=supplier)
        category = Category.objects.create(name="Test Category")
        product1 = Product.objects.create(name="Product 1", category=category)
        product2 = Product.objects.create(name="Product 2", category=category)

        ProductInfo.objects.create(
            product=product1, shop=shop, quantity=10, price=100, price_rrc=110
        )
        ProductInfo.objects.create(
            product=product2, shop=shop, quantity=12, price=110, price_rrc=120
        )

        url = reverse("product-list")
        response = api_client.get(url, {"shop": ""})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_products_with_invalid_shop_param_returns_all(
        self, api_client, supplier, shop
    ):
        """Тест: Фильтрация с невалидным параметром shop.

        Ожидаемый результат:
        - Статус ответа 200 (OK).
        - Возвращаются все доступные продукты.
        """
        api_client.force_authenticate(user=supplier)

        category = Category.objects.create(name="Test Category")
        product = Product.objects.create(name="Test Product", category=category)
        ProductInfo.objects.create(
            product=product,
            shop=shop,
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        url = reverse("product-list")
        response = api_client.get(url, {"shop": "invalid_shop"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_product_model_string_representation(self, product):
        """Тест: Строковое представление модели Product.

        Ожидаемый результат:
        - Строковое представление соответствует названию продукта.
        """
        assert str(product) == "Test Product"


@pytest.mark.django_db
class TestProductSerializer(TestCase):
    def setUp(self):
        self.shop = Shop.objects.create(name="Test Shop")
        self.category = Category.objects.create(name="Electronics")
        self.valid_data = {
            "name": "Test Product",
            "model": "X100",
            "category": "Electronics",
            "product_infos": [
                {
                    "shop": self.shop.id,
                    "quantity": 10,
                    "price": "999.99",
                    "parameters": {"Color": "Black", "Weight": "150g"},
                }
            ],
        }

    def test_create_product_with_new_category(self):
        """Тест: Создание продукта с новой категорией через сериализатор.

        Ожидаемый результат:
        - Создана новая категория.
        - Продукт успешно создан и связан с категорией.
        """
        data = self.valid_data.copy()
        data["category"] = "New Category"

        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        assert Product.objects.count() == 1
        assert Category.objects.get(name="New Category")
        assert product.product_infos.count() == 1

    def test_create_product_with_existing_category(self):
        """Тест: Создание продукта с существующей категорией через сериализатор.

        Ожидаемый результат:
        - Использована существующая категория.
        - Продукт успешно создан.
        """
        serializer = ProductSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        assert Category.objects.count() == 1
        assert product.category == self.category

    def test_parameters_are_created_for_product_info(self):
        """Тест: Создание параметров для информационного блока продукта.

        Ожидаемый результат:
        - Параметры успешно созданы и связаны с ProductInfo.
        """
        serializer = ProductSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        product_info = product.product_infos.first()
        assert product_info.product_parameters.count() == 2
        assert Parameter.objects.filter(name="Color").exists()

    def test_serializer_with_missing_required_fields_raises_error(self):
        """Тест: Валидация сериализатора с отсутствующими обязательными полями.

        Ожидаемый результат:
        - Вызывается ValidationError.
        - Сообщения об ошибках для отсутствующих полей.
        """
        invalid_data = self.valid_data.copy()
        del invalid_data["name"]
        del invalid_data["category"]

        serializer = ProductSerializer(data=invalid_data)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        errors = exc.value.detail
        assert "name" in errors
        assert "category" in errors
        assert "product_infos" not in errors

    def test_serializer_with_invalid_product_info_raises_error(self):
        """Тест: Валидация невалидных данных ProductInfo через сериализатор.

        Ожидаемый результат:
        - Вызывается ValidationError.
        - Сообщение об ошибке для невалидного поля цены.
        """
        invalid_data = self.valid_data.copy()
        invalid_data["product_infos"][0]["price"] = "-100"

        serializer = ProductSerializer(data=invalid_data)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)

        errors = exc.value.detail["product_infos"][0]
        assert "price" in errors

    def test_serializer_with_partial_product_info_uses_defaults(self):
        """Тест: Обработка частичных данных ProductInfo через сериализатор.

        Ожидаемый результат:
        - Отсутствующие поля заполняются значениями по умолчанию.
        - Продукт успешно создан.
        """
        data = self.valid_data.copy()
        data["product_infos"][0] = {"shop": self.shop.id, "price": "499.99"}

        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        product_info = product.product_infos.first()
        assert product_info.quantity == 0
        assert product_info.product_parameters.count() == 0
