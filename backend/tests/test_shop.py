import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Shop


@pytest.mark.django_db
class TestShopView:
    """Набор тестов для работы с магазинами через API."""

    def test_anonymous_user_can_view_shops(self, api_client):
        """
        Тест: Неавторизованный пользователь может просматривать список магазинов.
        Ожидаемый результат: Статус 200 OK.
        """
        response = api_client.get(reverse("shops"))
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_create_shop(self, api_client, admin):
        """
        Тест: Администратор может успешно создать новый магазин.
        Проверки:
        - Статус 201 Created
        - Корректное сохранение данных в БД
        - Автоматическая привязка к пользователю
        """
        api_client.force_authenticate(user=admin)
        data = {"name": "Admin Shop", "url": "http://admin.com"}

        response = api_client.post(reverse("shops"), data)
        assert response.status_code == status.HTTP_201_CREATED

        shop = Shop.objects.get(user=admin)
        assert shop.name == data["name"]
        assert shop.url == data["url"]

    def test_supplier_cannot_assign_other_user(self, api_client, customer, supplier):
        """
        Тест: Продавец не может указать другого пользователя при создании магазина.
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение об ошибке доступа
        """
        api_client.force_authenticate(user=supplier)
        data = {
            "name": "Supplier Shop",
            "url": "http://supplier.com",
            "user": customer.id,
        }

        response = api_client.post(reverse("shops"), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Указание пользователя доступно только администраторам"
            in response.data["user"]
        )

    def test_supplier_can_create_shop(self, api_client, supplier):
        """
        Тест: Продавец может создать магазин для себя.
        Проверки:
        - Статус 201 Created
        - Корректные данные в БД
        - Автоматическая привязка к текущему пользователю
        """
        api_client.force_authenticate(user=supplier)
        data = {"name": "Supplier Shop", "url": "http://supplier.com"}

        response = api_client.post(reverse("shops"), data)
        shop = Shop.objects.get(user=supplier)

        assert response.status_code == status.HTTP_201_CREATED
        assert shop.name == data["name"]
        assert shop.url == data["url"]

    def test_admin_cannot_create_duplicate_shop(self, api_client, admin):
        """
        Тест: Администратор не может создать дубликат магазина (повторное название для одного пользователя).
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение о дубликате
        """
        api_client.force_authenticate(user=admin)
        Shop.objects.create(name="Existing", url="http://existing.com", user=admin)

        response = api_client.post(
            reverse("shops"), {"name": "Existing", "url": "http://new.com"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Магазин с таким названием уже существует" in response.data["name"]

    def test_supplier_cannot_create_duplicate_shop(self, api_client, supplier):
        """
        Тест: Продавец не может создать два магазина с одинаковым названием.
        Ожидаемый результат при повторном запросе:
        - Статус 400 Bad Request
        - Сообщение о дубликате
        """
        api_client.force_authenticate(user=supplier)
        data = {"name": "SupplierShop", "url": "http://supplier.com"}

        api_client.post(reverse("shops"), data)
        response = api_client.post(reverse("shops"), data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Магазин с таким названием уже существует" in response.data["name"]

    def test_supplier_cannot_use_existing_shop_name(self, api_client, admin, supplier):
        """
        Тест: Продавец не может использовать название магазина, существующее у другого пользователя.
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение о конфликте имен
        """
        api_client.force_authenticate(user=admin)
        Shop.objects.create(name="Existing", url="http://admin.com", user=admin)

        api_client.force_authenticate(user=supplier)
        response = api_client.post(
            reverse("shops"), {"name": "Existing", "url": "http://supplier.com"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Магазин с таким названием уже существует у другого продавца"
            in response.data["name"]
        )

    def test_customer_cannot_create_shop(self, api_client, customer):
        """
        Тест: Покупатель не может создать магазин.
        Ожидаемый результат:
        - Статус 403 Forbidden
        - Сообщение о недостатке прав
        """
        api_client.force_authenticate(user=customer)
        response = api_client.post(
            reverse("shops"), {"name": "Customer Shop", "url": "http://customer.com"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "недостаточно прав" in str(response.data["detail"]).lower()

    def test_shop_string_representation(self, shop):
        """
        Тест: Строковое представление магазина соответствует ожидаемому формату.
        Ожидаемый формат: <название магазина>
        """
        assert str(shop) == shop.name
