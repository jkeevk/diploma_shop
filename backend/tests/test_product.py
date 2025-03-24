import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Product, Category, Shop, ProductInfo

@pytest.mark.django_db
class TestProductAPI:
    def test_read_product(self, api_client, supplier, shop):
        """
        Тест получения информации о товаре через API.
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
        assert response.data["category"]["name"] == "Test Category"
        assert len(response.data["product_infos"]) == 1
        assert response.data["product_infos"][0]["shop"] == shop.id
        assert response.data["product_infos"][0]["quantity"] == 10

    def test_create_product_with_infos(self, api_client, supplier, shop):
        """
        Тест на создание продукта с вложенными данными через API.
        """
        api_client.force_authenticate(user=supplier)
        product_data = {
            "name": "Test Product",
            "model": "Test Model",
            "category": {"name": "New_Category"},
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
        assert response.data["category"]["name"] == "New_Category"
        assert len(response.data["product_infos"]) == 1
        assert response.data["product_infos"][0]["shop"] == shop.id
        assert response.data["product_infos"][0]["quantity"] == 10

    def test_update_product_with_updated_product_info(self, api_client, supplier, shop):
        """
        Тест на обновление продукта с изменением информации о продукте через API.
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
                    "id": product_info.id,
                    "shop": new_shop.id,
                    "quantity": 20,
                    "price": 200.00,
                    "price_rrc": 220.00,
                }
            ],
        }

        url = reverse("product-detail", kwargs={"pk": product.id})
        response = api_client.patch(url, update_data, format="json")
        assert response.status_code == status.HTTP_200_OK

        updated_info = ProductInfo.objects.get(product=product, shop=new_shop)
        assert updated_info.shop.id == new_shop.id
        assert updated_info.quantity == 20

    def test_filter_by_shop(self, api_client, product, supplier, shop, category):
        """
        Тест фильтрации продуктов по магазину через API.
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
        assert response.data[0]["category"]["name"] == "Test Category"
        assert len(response.data[0]["product_infos"]) == 1
        assert response.data[0]["product_infos"][0]["shop"] == shop.id

    def test_create_product_without_required_fields(self, api_client, supplier):
        """
        Тест на создание продукта без обязательных полей через API.
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

    def test_update_non_existent_product(self, api_client, supplier):
        """
        Тест на обновление несуществующего продукта через API.
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

    def test_delete_product(self, api_client, supplier, shop):
        """
        Тест на удаление продукта через API.
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

    def test_get_non_existent_product(self, api_client, supplier):
        """
        Тест на получение несуществующего продукта через API.
        """
        api_client.force_authenticate(user=supplier)

        url = reverse("product-detail", kwargs={"pk": 999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_by_shop_without_shop_param(self, api_client, supplier, shop):
        """
        Тест фильтрации продуктов без указания магазина.
        Должен вернуть все продукты.
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

    def test_filter_by_non_existent_shop(self, api_client, supplier):
        """
        Тест фильтрации по несуществующему магазину.
        Должен вернуть пустой список.
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

    def test_filter_by_category(self, api_client, supplier):
        """
        Тест фильтрации продуктов по категории.
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

    def test_filter_by_existing_shop(self, api_client, supplier):
        """
        Тест фильтрации по существующему магазину.
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

    def test_filter_shop_empty_value(self, api_client, supplier, shop):
        """
        Тест фильтрации с пустым значением shop, должен вернуть все продукты.
        """
        api_client.force_authenticate(user=supplier)
        category = Category.objects.create(name="Test Category")
        product1 = Product.objects.create(name="Product 1", category=category)
        product2 = Product.objects.create(name="Product 2", category=category)
        
        ProductInfo.objects.create(product=product1, shop=shop, quantity=10, price=100, price_rrc=110)
        ProductInfo.objects.create(product=product2, shop=shop, quantity=12, price=110, price_rrc=120)

        url = reverse("product-list")
        response = api_client.get(url, {"shop": ""})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_shop_invalid_value(self, api_client, supplier, shop):
        """
        Тест фильтрации с невалидным shop (не число).
        Проверяет, что возвращается исходный queryset.
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

    def test_product_str_method(self, product):
        """
        Тестирование строкового представления объекта Product
        """
        assert str(product) == "Test Product"

