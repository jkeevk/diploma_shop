import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Contact


@pytest.mark.django_db
class TestUserContacts:
    """
    Тесты для работы с контактами пользователя.
    """

    def test_create_contact(self, api_client, customer):
        """
        Тест создания контакта.
        """
        api_client.force_authenticate(user=customer)

        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "structure": "1",
            "building": "A",
            "apartment": "15",
            "phone": "+79991234567",
            "user": customer.id,
        }

        url = reverse("user-contacts-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        contact = Contact.objects.get(user=customer)
        assert contact.city == "Moscow"
        assert contact.street == "Lenina"
        assert contact.house == "10"
        assert contact.structure == "1"
        assert contact.building == "A"
        assert contact.apartment == "15"
        assert contact.phone == "+79991234567"

    def test_create_contact_with_invalid_phone(self, api_client, customer):
        """
        Тест создания контакта с неверным номером телефона.
        """
        api_client.force_authenticate(user=customer)

        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "structure": "1",
            "building": "A",
            "apartment": "15",
            "phone": "invalid_phone",
            "user": customer.id,
        }

        url = reverse("user-contacts-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone" in response.data

    def test_create_max_contacts(self, api_client, customer):
        """
        Тест создания максимального количества контактов (5).
        """
        api_client.force_authenticate(user=customer)

        for i in range(5):
            Contact.objects.create(
                user=customer,
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
            "user": customer.id,
        }

        url = reverse("user-contacts-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert (
            "Максимум 5 адресов на пользователя."
            in response.data["non_field_errors"][0]
        )

    def test_delete_contact(self, api_client, customer, contact):
        """
        Тест удаления контакта.
        """
        api_client.force_authenticate(user=customer)

        url = reverse("user-contacts-detail", args=[contact.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Contact.objects.filter(id=contact.id).exists()
