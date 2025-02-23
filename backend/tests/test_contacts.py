import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import Contact, User


@pytest.mark.django_db
class TestUserContacts:
    """
    Тесты для работы с контактами пользователя.
    """

    def setup_method(self):
        """
        Инициализация клиента и пользователя перед каждым тестом.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            first_name="Test",
            last_name="User",
            role="customer",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_contact(self):
        """
        Тест создания контакта.
        """
        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "structure": "1",
            "building": "A",
            "apartment": "15",
            "phone": "+79991234567",
            "user": self.user.id,
        }

        url = reverse("user-contacts-list")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        contact = Contact.objects.get(user=self.user)
        assert contact.city == "Moscow"
        assert contact.street == "Lenina"
        assert contact.house == "10"
        assert contact.structure == "1"
        assert contact.building == "A"
        assert contact.apartment == "15"
        assert contact.phone == "+79991234567"

    def test_create_contact_with_invalid_phone(self):
        """
        Тест создания контакта с неверным номером телефона.
        """
        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "structure": "1",
            "building": "A",
            "apartment": "15",
            "phone": "invalid_phone",
            "user": self.user.id,
        }

        url = reverse("user-contacts-list")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone" in response.data

    def test_create_max_contacts(self):
        """
        Тест создания максимального количества контактов (5).
        """
        for i in range(5):
            Contact.objects.create(
                user=self.user,
                city=f"City {i}",
                street=f"Street {i}",
                house=f"{i}",
                structure=f"{i}",
                building=f"{i}",
                apartment=f"{i}",
                phone=f"+7999123456{i}",
            )

        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "structure": "1",
            "building": "A",
            "apartment": "15",
            "phone": "+79991234567",
            "user": self.user.id,
        }

        url = reverse("user-contacts-list")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert (
            "Максимум 5 адресов на пользователя."
            in response.data["non_field_errors"][0]
        )

    def test_delete_contact(self):
        """
        Тест удаления контакта.
        """
        contact = Contact.objects.create(
            user=self.user,
            city="Moscow",
            street="Lenina",
            house="10",
            structure="1",
            building="A",
            apartment="15",
            phone="+79991234567",
        )

        url = reverse("user-contacts-detail", args=[contact.id])
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Contact.objects.filter(id=contact.id).exists()
