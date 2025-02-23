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
            username="testuser",
            password="testpassword"
        )

    def test_create_contact(self):
        """
        Тест создания контакта.
        """
        url = reverse("user-contacts-list", kwargs={"user_pk": self.user.pk})
        data = {
            "name": "Test Contact",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Contact.objects.filter(name="Test Contact").exists()

    def test_list_contacts(self):
        """
        Тест получения списка контактов.
        """
        Contact.objects.create(name="Contact One", phone="1234567890", user=self.user)
        Contact.objects.create(name="Contact Two", phone="0987654321", user=self.user)

        url = reverse("user-contacts-list", kwargs={"user_pk": self.user.pk})
        response = self.client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_contact(self):
        """
        Тест получения конкретного контакта.
        """
        contact = Contact.objects.create(name="Test Contact", phone="1234567890", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "id": contact.pk})
        response = self.client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Contact"
        assert response.data["phone"] == "1234567890"

    def test_update_contact(self):
        """
        Тест обновления контакта.
        """
        contact = Contact.objects.create(name="Test Contact", phone="1234567890", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "id": contact.pk})
        updated_data = {
            "name": "Updated Contact",
            "phone": "9876543210"
        }
        response = self.client.put(url, updated_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        contact.refresh_from_db()
        assert contact.name == "Updated Contact"
        assert contact.phone == "9876543210"

    def test_partial_update_contact(self):
        """
        Тест частичного обновления контакта.
        """
        contact = Contact.objects.create(name="Test Contact", phone="1234567890", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "id": contact.pk})
        partial_data = {"phone": "1112223333"}
        response = self.client.patch(url, partial_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        contact.refresh_from_db()
        assert contact.phone == "1112223333"

    def test_delete_contact(self):
        """
        Тест удаления контакта.
        """
        contact = Contact.objects.create(name="Test Contact", phone="1234567890", user=self.user)

        url = reverse("user-contacts-detail", kwargs={"user_pk": self.user.pk, "id": contact.pk})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Contact.objects.filter(id=contact.id).exists()
