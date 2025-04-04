import pytest
from backend.models import Contact
from backend.serializers import ContactSerializer
from rest_framework.exceptions import ErrorDetail
from django.urls import reverse
from rest_framework import status
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from backend.validators import PhoneValidator


@pytest.mark.django_db
class TestContactSerializer:
    """Тесты для сериализатора ContactSerializer."""

    def test_serializer_auto_set_user_for_non_admin(self, customer):
        """Тест автоматического назначения пользователя при создании (не администратор).

        Ожидаемый результат:
        - Контакт должен быть связан с текущим пользователем.
        - Статус ответа: 200 OK
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
        """Тест валидации при несовпадении пользователя (не администратор).

        Ожидаемый результат:
        - Ошибка: нельзя указать другого пользователя.
        - Статус ответа: 400 Bad Request
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
        """Тест, что админ может указать любого пользователя.

        Ожидаемый результат:
        - Админ может указать другого пользователя.
        - Статус ответа: 200 OK
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
        """Тест интеграции с моделью (вызов clean()).

        Ожидаемый результат:
        - Ошибка: максимальное количество адресов для пользователя — 5.
        - Статус ответа: 400 Bad Request
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
        """Тест, что при частичном обновлении пользователь остается прежним.

        Ожидаемый результат:
        - Пользователь не изменится после частичного обновления контакта.
        - Статус ответа: 200 OK
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
        """Тестирование строкового представления контакта.

        Ожидаемый результат:
        - Контакт должен выводиться в формате 'city street house'.
        - Статус ответа: 200 OK
        """
        assert f"{contact.city} {contact.street} {contact.house}" == str(contact)


@pytest.mark.django_db
class TestContactViewSet:
    """Тесты для ContactViewSet."""

    def test_admin_sees_all_contacts(self, api_client, admin, customer, supplier):
        """Проверка, что администратор видит все контакты.

        Ожидаемый результат:
        - Ответ должен содержать все контакты (2).
        - Статус ответа: 200 OK
        """
        Contact.objects.create(user=customer, city="Moscow", street="Lenina", house="1")
        Contact.objects.create(user=supplier, city="SPb", street="Nevsky", house="5")

        api_client.force_authenticate(user=admin)
        response = api_client.get(reverse("user-contacts-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_non_admin_sees_only_own_contacts(self, api_client, customer, supplier):
        """Проверка, что не-администратор видит только свои контакты.

        Ожидаемый результат:
        - Ответ должен содержать только контакт текущего пользователя.
        - Статус ответа: 200 OK
        """
        Contact.objects.create(user=customer, city="Moscow", street="Arbat", house="10")
        Contact.objects.create(user=supplier, city="SPb", street="Main", house="3")

        api_client.force_authenticate(user=customer)
        response = api_client.get(reverse("user-contacts-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["user"] == customer.id

        api_client.force_authenticate(user=supplier)
        response = api_client.get(reverse("user-contacts-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["user"] == supplier.id


@pytest.mark.django_db
class TestContactFilter:
    """Тестирование фильтрации контактов по пользователю."""

    def test_admin_can_filter_by_user(self, api_client, admin, customer, supplier):
        """Тест, что админ может фильтровать контакты по пользователю.

        Ожидаемый результат:
        - Админ может фильтровать контакты по ID пользователя.
        - Статус ответа: 200 OK
        """
        customer_contact = Contact.objects.create(
            user=customer, city="Moscow", phone="+79991112233"
        )
        supplier_contact = Contact.objects.create(
            user=supplier, city="SPb", phone="+79992223344"
        )

        api_client.force_authenticate(user=admin)

        response = api_client.get(reverse("user-contacts-list"), {"user": customer.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == customer_contact.id

        response = api_client.get(reverse("user-contacts-list"), {"user": supplier.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == supplier_contact.id

    def test_non_admin_cannot_filter_by_user(self, api_client, customer, supplier):
        """Тест, что обычные пользователи не могут фильтровать по пользователю.

        Ожидаемый результат:
        - Ответ должен быть 403 при попытке фильтровать по пользователю.
        - Статус ответа: 403 Forbidden
        """
        Contact.objects.create(user=supplier, city="SPb")

        api_client.force_authenticate(user=customer)
        response = api_client.get(reverse("user-contacts-list"), {"user": supplier.id})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Фильтрация по пользователю доступна только администраторам" in str(
            response.data
        )

        api_client.force_authenticate(user=supplier)
        response = api_client.get(reverse("user-contacts-list"), {"user": customer.id})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_by_nonexistent_user(self, api_client, admin):
        """Тест, что фильтрация по несуществующему пользователю вызывает ошибку.

        Ожидаемый результат:
        - Ответ должен быть 400 с ошибкой о несуществующем пользователе.
        - Статус ответа: 400 Bad Request
        """
        api_client.force_authenticate(user=admin)

        response = api_client.get(reverse("user-contacts-list"), {"user": 9999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["user"][0] == "Пользователь с ID 9999 не существует"


@pytest.mark.django_db
class TestPhoneValidator:
    """Тестирование PhoneValidator."""

    @pytest.fixture
    def validator(self):
        return PhoneValidator()

    def test_null_value(self, validator):
        """Тест, что None значение вызывает ошибку.

        Ожидаемый результат:
        - Ошибка: номер телефона не может быть пустым.
        """
        with pytest.raises(ValidationError) as excinfo:
            validator(None)
        assert str(excinfo.value) == "['Номер телефона не может быть пустым']"

    def test_non_string_input(self, validator):
        """Тест, что нестроковые значения вызывают ошибку.

        Ожидаемый результат:
        - Ошибка: номер телефона должен быть строкой.
        """
        test_cases = [79991234567, True, {"phone": "+79991234567"}, ["+79991234567"]]

        for value in test_cases:
            with pytest.raises(ValidationError) as excinfo:
                validator(value)
            assert str(excinfo.value) == "['Номер телефона должен быть строкой']"

    def test_valid_numbers(self, validator):
        """Тест на проверку валидных номеров телефона.

        Ожидаемый результат:
        - Номер телефона должен быть принят валидным.
        """
        valid_numbers = ["+79991234567", "+1234567890", "+12345678901234567890"]
        for number in valid_numbers:
            validator(number)

    def test_invalid_numbers(self, validator):
        """Тест на проверку невалидных номеров.

        Ожидаемый результат:
        - Ошибка с соответствующим сообщением при неправильном номере.
        """
        test_cases = [
            ("79991234567", "Номер должен начинаться с '+'"),
            ("+123", "Слишком короткий номер"),
            ("+7abc999123", "Номер должен содержать только цифры после '+'"),
        ]

        for number, expected_error in test_cases:
            with pytest.raises(ValidationError) as excinfo:
                validator(number)
            assert expected_error in str(excinfo.value)

    def test_get_nonexistent_contact(self, api_client, admin):
        """Тест получения несуществующего контакта.

        Ожидаемый результат:
        - Ошибка 404 при попытке получения несуществующего контакта.
        - Статус ответа: 404 Not Found
        """
        api_client.force_authenticate(user=admin)
        response = api_client.get(reverse("user-contacts-detail", kwargs={"pk": 9999}))

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "Контакт не найден"
