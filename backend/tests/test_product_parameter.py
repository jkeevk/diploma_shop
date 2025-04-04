import pytest
from django.db import IntegrityError
from backend.models import ProductParameter


@pytest.mark.django_db
class TestProductParameter:
    """
    Тесты для модели ProductParameter.
    """

    def test_create_product_parameter_success(self, product_info, parameter):
        """
        Тест успешного создания параметра товара.

        Ожидаемый результат: параметр товара создается с заданными значениями.
        """
        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        assert product_parameter.product_info == product_info
        assert product_parameter.parameter == parameter
        assert product_parameter.value == "Test Value"

    def test_update_product_parameter_value(self, product_info, parameter):
        """
        Тест обновления значения существующего параметра товара.

        Ожидаемый результат: значение параметра обновляется на новое значение.
        """
        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        product_parameter.value = "Updated Value"
        product_parameter.save()

        assert product_parameter.value == "Updated Value"

    def test_delete_product_parameter_success(self, product_info, parameter):
        """
        Тест успешного удаления параметра товара.

        Ожидаемый результат: параметр товара удаляется из базы данных.
        """
        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        product_parameter_id = product_parameter.id
        product_parameter.delete()

        assert not ProductParameter.objects.filter(id=product_parameter_id).exists()

    def test_create_product_parameter_missing_required_fields(self, parameter):
        """
        Тест создания параметра товара без обязательных полей вызывает ошибку.

        Ожидаемый результат: возникает исключение при попытке создания.
        """
        with pytest.raises(Exception):
            ProductParameter.objects.create(
                parameter=parameter,
                value="Test Value",
            )

    def test_create_duplicate_product_parameter_raises_integrity_error(
        self, product_info, parameter
    ):
        """
        Тест, что создание дубликата параметра товара вызывает IntegrityError.

        Ожидаемый результат: возникает исключение IntegrityError при попытке создания дубликата.
        """
        ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        with pytest.raises(IntegrityError):
            ProductParameter.objects.create(
                product_info=product_info,
                parameter=parameter,
                value="Test Value",
            )

    def test_product_parameter_str_method_returns_expected_string(
        self, product_parameter
    ):
        """
        Проверяет, что метод __str__ возвращает ожидаемую строку представления
        экземпляра ProductParameter.

        Ожидаемый формат: "<имя_параметра>: <значение>"
        """

        assert (
            str(product_parameter)
            == f"{product_parameter.parameter.name}: {product_parameter.value}"
        )
