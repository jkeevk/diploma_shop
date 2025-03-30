import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import User, Contact, Order, OrderItem
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestContactUserCRUD:
    """
    Тесты для CRUD операций с контактами пользователей через связанную модель.
    """

    def setup_method(self):
        """
        Инициализация клиента и создание пользователя перед каждым тестом.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="strongpassword123",
            first_name="User",
            last_name="Test",
            role="customer",
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_contact(self):
        """
        Тест создания контакта.
        """
        url = reverse("user-contacts-list", kwargs={"user_pk": self.user.pk})
        data = {
            "city": "Test City",
            "street": "Test Street",
            "house": "123",
            "phone": "+79991234567",
            "user": self.user.pk,
        }
        response = self.client.post(url, data, format="json")

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Ожидался статус 201, получен {response.status_code}. Ответ: {response.data}"
        assert Contact.objects.filter(city="Test City").exists()

    def test_list_contacts(self):
        """
        Тест получения списка контактов.
        """
        Contact.objects.create(
            city="City1",
            street="Street1",
            house="123",
            phone="+79991234567",
            user=self.user,
        )
        Contact.objects.create(
            city="City2",
            street="Street2",
            house="456",
            phone="+79997654321",
            user=self.user,
        )

        url = reverse("user-contacts-list", kwargs={"user_pk": self.user.pk})
        response = self.client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_contact(self):
        """
        Тест получения конкретного контакта.
        """
        contact = Contact.objects.create(
            city="Test City",
            street="Test Street",
            house="123",
            phone="+79991234567",
            user=self.user,
        )

        url = reverse(
            "user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk}
        )
        response = self.client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["city"] == "Test City"
        assert response.data["phone"] == "+79991234567"

    def test_update_contact(self):
        """
        Тест обновления контакта.
        """
        contact = Contact.objects.create(
            city="Test City",
            street="Test Street",
            house="123",
            phone="+79991234567",
            user=self.user,
        )

        url = reverse(
            "user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk}
        )
        updated_data = {
            "city": "Updated City",
            "street": "Updated Street",
            "house": "456",
            "phone": "+79991111111",
            "user": self.user.pk,
        }
        response = self.client.put(url, updated_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        contact.refresh_from_db()
        assert contact.city == "Updated City"
        assert contact.phone == "+79991111111"

    def test_partial_update_contact(self):
        """
        Тест частичного обновления контакта.
        """
        contact = Contact.objects.create(
            city="Test City",
            street="Test Street",
            house="123",
            phone="+79991234567",
            user=self.user,
        )

        url = reverse(
            "user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk}
        )
        partial_data = {"phone": "+79991111111", "user": self.user.pk}
        response = self.client.patch(url, partial_data, format="json")

        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Ожидался статус 200, получен {response.status_code}. Ответ: {response.data}"
        contact.refresh_from_db()
        assert contact.phone == "+79991111111"

    def test_delete_contact(self):
        """
        Тест удаления контакта.
        """
        contact = Contact.objects.create(
            city="Test City",
            street="Test Street",
            house="123",
            phone="+79991234567",
            user=self.user,
        )

        url = reverse(
            "user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk}
        )
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Contact.objects.filter(id=contact.id).exists()


@pytest.mark.django_db
class TestUserOrdersView:
    """
    Тесты для получения списка заказов покупателя.
    """

    def test_get_orders_authenticated(
        self, contact, api_client, customer, order, product, shop
    ):
        """Тест получения заказов для авторизованного пользователя."""
        api_client.force_authenticate(user=customer)
        order = Order.objects.create(user=customer)
        order_item = OrderItem.objects.create(
            order=order, product=product, shop=shop, quantity=2
        )
        url = reverse("confirm-basket", args=[contact.id])

        response = api_client.post(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "Заказ успешно подтвержден."}
        response = api_client.get(reverse("user-orders"))

        order.refresh_from_db()
        assert order.status == "confirmed"
        assert order_item.product.name == "Test Product"
        assert order_item.product.category.name == "Test Category"
        assert order_item.quantity == 2

        assert response.status_code == status.HTTP_200_OK

        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert response.data[0]["id"] == order.id

    def test_get_orders_anonymous(self, api_client):
        """Тест получения заказов для анонимного пользователя."""
        response = api_client.get(reverse("user-orders"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"
        assert "Пожалуйста, войдите в систему." == response.data["detail"]


@pytest.mark.django_db
class TestUserManager:

    User = get_user_model()

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_manager = User.objects

    def test_create_user_with_email(self):
        """Тест создания пользователя с email."""
        user = self.user_manager.create_user(
            email="test@example.com", password="password123"
        )
        assert user.email == "test@example.com"
        assert user.check_password("password123")
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_without_email(self):
        """Тест создания пользователя без email."""
        with pytest.raises(ValueError, match="Поле Email должно быть заполнено"):
            self.user_manager.create_user(email="", password="password123")

    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        superuser = self.user_manager.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        assert superuser.email == "admin@example.com"
        assert superuser.check_password("adminpass")
        assert superuser.is_staff
        assert superuser.is_superuser

    def test_create_superuser_without_is_staff(self):
        """Тест создания суперпользователя без is_staff."""
        with pytest.raises(
            ValueError, match="Суперпользователь должен иметь is_staff=True."
        ):
            self.user_manager.create_superuser(
                email="admin@example.com", password="adminpass", is_staff=False
            )

    def test_create_superuser_without_is_superuser(self):
        """Тест создания суперпользователя без is_superuser."""
        with pytest.raises(
            ValueError, match="Суперпользователь должен иметь is_superuser=True."
        ):
            self.user_manager.create_superuser(
                email="admin@example.com", password="adminpass", is_superuser=False
            )

    def test_user_str_method(self, customer_login):
        """Тест строкового представления пользователя."""
        assert str(customer_login) == "customer@example.com"
