import pytest
from backend.models import Contact
from backend.serializers import ContactSerializer
from rest_framework.exceptions import ErrorDetail


@pytest.mark.django_db
class TestContactSerializer:
    """
    Тесты для сериализатора ContactSerializer.
    """

    def test_serializer_auto_set_user_for_non_admin(self, customer):
        """
        Тест автоматического назначения пользователя при создании (не админ).
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
        Тест валидации при несовпадении пользователя (не админ).
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
