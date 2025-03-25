import pytest
from django.db import IntegrityError
from backend.models import ProductParameter


@pytest.mark.django_db
class TestProductParameter:
    """
    Тесты для модели ProductParameter.
    """

    def test_create_product_parameter(self, product_info, parameter):
        """
        Тест создания параметра товара.
        """
        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        assert product_parameter.product_info == product_info
        assert product_parameter.parameter == parameter
        assert product_parameter.value == "Test Value"

    def test_update_product_parameter(self, product_info, parameter):
        """
        Тест обновления параметра товара.
        """

        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        product_parameter.value = "Updated Value"
        product_parameter.save()

        assert product_parameter.value == "Updated Value"

    def test_delete_product_parameter(self, product_info, parameter):
        """
        Тест удаления параметра товара.
        """

        product_parameter = ProductParameter.objects.create(
            product_info=product_info,
            parameter=parameter,
            value="Test Value",
        )

        product_parameter_id = product_parameter.id
        product_parameter.delete()

        assert not ProductParameter.objects.filter(id=product_parameter_id).exists()

    def test_create_product_parameter_without_required_fields(
        self, product_info, parameter
    ):
        """
        Тест создания параметра товара без обязательных полей.
        """

        with pytest.raises(Exception):
            ProductParameter.objects.create(
                parameter=parameter,
                value="Test Value",
            )

    def test_create_duplicate_product_parameter(self, product_info, parameter):
        """
        Тест создания дубликата параметра товара.
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

    def test_product_parameter_str_method(self, product_parameter):
        """
        Проверяет, что метод __str__ у параметра возвращает ожидаемую строку.
        Ожидается, что строковое представление параметра равно "Test Parameter".
        """
        assert (
            str(product_parameter)
            == f"{product_parameter.parameter.name}: {product_parameter.value}"
        )
