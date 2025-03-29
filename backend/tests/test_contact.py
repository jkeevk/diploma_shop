import pytest
from backend.models import Contact
from backend.serializers import ContactSerializer
from rest_framework.exceptions import ErrorDetail
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestContactSerializer:
    """
    Тесты для сериализатора ContactSerializer.
    """

    def test_serializer_auto_set_user_for_non_admin(self, customer):
        """
        Тест автоматического назначения пользователя при создании (не администратор).
        """
        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "phone": "+79991234567",
        }

        serializer = ContactSerializer(
            data=data, context={"request": type("Request", (), {"user": customer})}
        )

        assert serializer.is_valid()
        contact = serializer.save()
        assert contact.user == customer

    def test_serializer_validate_user_mismatch(self, customer, supplier):
        """
        Тест валидации при несовпадении пользователя (не администратор).
        """
        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "phone": "+79991234567",
            "user": supplier.id,
        }

        serializer = ContactSerializer(
            data=data, context={"request": type("Request", (), {"user": customer})}
        )

        assert not serializer.is_valid()
        assert serializer.errors == {
            "user": [
                ErrorDetail(
                    string="Вы не можете указывать другого пользователя.",
                    code="invalid",
                )
            ]
        }

    def test_serializer_admin_can_set_any_user(self, admin, customer):
        """
        Тест что админ может указать любого пользователя.
        """
        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "phone": "+79991234567",
            "user": customer.id,
        }

        serializer = ContactSerializer(
            data=data, context={"request": type("Request", (), {"user": admin})}
        )

        assert serializer.is_valid()
        contact = serializer.save()
        assert contact.user == customer

    def test_serializer_model_validation(self, customer):
        """
        Тест интеграции с моделью (вызов clean()).
        """
        Contact.objects.bulk_create(
            [
                Contact(
                    user=customer,
                    city=f"City {i}",
                    street=f"Street {i}",
                    house=str(i),
                    phone=f"+7999123456{i}",
                )
                for i in range(5)
            ]
        )

        data = {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "phone": "+79991234567",
            "user": customer.id,
        }

        serializer = ContactSerializer(
            data=data, context={"request": type("Request", (), {"user": customer})}
        )

        assert not serializer.is_valid()
        assert serializer.errors == {
            "non_field_errors": [
                ErrorDetail(
                    string="Максимум 5 адресов на пользователя.", code="invalid"
                )
            ]
        }

    def test_partial_update_keep_existing_user(self, customer, contact):
        """
        Тест что при частичном обновлении пользователь остается прежним.
        """
        new_phone = "+79991111111"
        serializer = ContactSerializer(
            instance=contact,
            data={"phone": new_phone},
            partial=True,
            context={"request": type("Request", (), {"user": customer})},
        )

        assert serializer.is_valid()
        updated_contact = serializer.save()
        assert updated_contact.user == contact.user
        assert updated_contact.phone == new_phone

    def test_contact_str_method(self, contact):
        """
        Тестирование строкового представления контакта.
        """
        assert f"{contact.city} {contact.street} {contact.house}" == str(contact)


@pytest.mark.django_db
class TestContactViewSet:
    """
    Тесты для ContactViewSet.
    """

    def test_admin_sees_all_contacts(self, api_client, admin, customer, supplier):
        """
        Проверяем, что администратор получает все контакты.
        """
        Contact.objects.create(user=customer, city="Moscow", street="Lenina", house="1")
        Contact.objects.create(user=supplier, city="SPb", street="Nevsky", house="5")

        api_client.force_authenticate(user=admin)
        response = api_client.get(reverse("user-contacts-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_non_admin_sees_only_own_contacts(self, api_client, customer, supplier):
        """
        Проверяем, что не-администратор (customer/supplier) видит только свои контакты.
        """
        Contact.objects.create(user=customer, city="Moscow", street="Arbat", house="10")
        Contact.objects.create(user=supplier, city="SPb", street="Main", house="3")

        api_client.force_authenticate(user=customer)
        response = api_client.get(reverse("user-contacts-list"))
        assert len(response.data) == 1
        assert response.data[0]["user"] == customer.id

        api_client.force_authenticate(user=supplier)
        response = api_client.get(reverse("user-contacts-list"))
        assert len(response.data) == 1
        assert response.data[0]["user"] == supplier.id
