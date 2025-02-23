import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import User, Contact


@pytest.mark.django_db
class TestUserRegistration:
    """
    Тесты для регистрации пользователя.
    """

    def setup_method(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()

    def test_register_user_without_email_confirmation(self):
        """
        Тест регистрации пользователя без подтверждения email.
        """
        data = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
        }

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.get(email="test@example.com")
        assert user is not None
        assert user.role == "customer"

    def test_register_user_with_wrong_role(self):
        """
        Тест регистрации пользователя с неверной ролью.
        """
        data = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "invalid_role",
        }

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "role" in response.data

    def test_register_user_with_existing_email(self):
        """
        Тест регистрации пользователя с уже существующим email.
        """
        User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            first_name="Test",
            last_name="User",
            role="customer",
        )

        data = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
        }

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_user_without_required_fields(self):
        """
        Тест регистрации пользователя без обязательных полей.
        """
        data = {}

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "password" in response.data
        assert "role" in response.data

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
            email="user@example.com",  # Обязательный аргумент
            password="strongpassword123",
            first_name="User",
            last_name="Test",
            role="customer",
            is_active=True
        )
        self.client.force_authenticate(user=self.user)  # Аутентификация пользователя

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
            "user": self.user.pk  # Добавляем поле user
        }
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Ожидался статус 201, получен {response.status_code}. Ответ: {response.data}"
        assert Contact.objects.filter(city="Test City").exists()

    def test_list_contacts(self):
        """
        Тест получения списка контактов.
        """
        Contact.objects.create(city="City1", street="Street1", house="123", phone="+79991234567", user=self.user)
        Contact.objects.create(city="City2", street="Street2", house="456", phone="+79997654321", user=self.user)

        url = reverse("user-contacts-list", kwargs={"user_pk": self.user.pk})
        response = self.client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_contact(self):
        """
        Тест получения конкретного контакта.
        """
        contact = Contact.objects.create(city="Test City", street="Test Street", house="123", phone="+79991234567", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk})
        response = self.client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["city"] == "Test City"
        assert response.data["phone"] == "+79991234567"

    def test_update_contact(self):
        """
        Тест обновления контакта.
        """
        contact = Contact.objects.create(city="Test City", street="Test Street", house="123", phone="+79991234567", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk})
        updated_data = {
            "city": "Updated City",
            "street": "Updated Street",
            "house": "456",
            "phone": "+79991111111",
            "user": self.user.pk  # Добавляем поле user
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
        contact = Contact.objects.create(city="Test City", street="Test Street", house="123", phone="+79991234567", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk})
        partial_data = {"phone": "+79991111111"}
        response = self.client.patch(url, partial_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        contact.refresh_from_db()
        assert contact.phone == "+79991111111"

    def test_delete_contact(self):
        """
        Тест удаления контакта.
        """
        contact = Contact.objects.create(city="Test City", street="Test Street", house="123", phone="+79991234567", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "pk": contact.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Contact.objects.filter(id=contact.id).exists()
