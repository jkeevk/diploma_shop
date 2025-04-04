import pytest
from backend.models import ProductInfo
from django.core.exceptions import ValidationError
from decimal import Decimal


@pytest.mark.django_db
class TestProductInfo:
    """
    Тесты для модели ProductInfo.
    """

    def test_create_product_info(self, shop, product):
        """
        Тест создания информации о товаре.

        Ожидаемый результат: информация о товаре создается с заданными значениями.
        """
        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            description="Test Description",
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        assert product_info.product == product
        assert product_info.shop == shop
        assert product_info.description == "Test Description"
        assert product_info.quantity == 10
        assert product_info.price == 100.00
        assert product_info.price_rrc == 120.00

    def test_product_info_unique_together(self, shop, product):
        """
        Тест, проверяющий уникальность сочетания продукта и магазина в ProductInfo.

        Ожидаемый результат: возникает исключение при попытке создать дубликат.
        """
        product_info1 = ProductInfo.objects.create(
            product=product,
            shop=shop,
            description="Test Description 1",
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        with pytest.raises(Exception):
            ProductInfo.objects.create(
                product=product,
                shop=shop,
                description="Test Description 2",
                quantity=20,
                price=200.00,
                price_rrc=220.00,
            )

    def test_product_info_price_validation(self, shop, product):
        """
        Тест для проверки валидации цены.

        Ожидаемый результат: возникает исключение ValidationError при отрицательной цене.
        """
        with pytest.raises(ValidationError):
            product_info = ProductInfo(
                product=product,
                shop=shop,
                description="Test Description",
                quantity=10,
                price=-100.00,
                price_rrc=120.00,
            )
            product_info.clean()

    def test_product_info_quantity_validation(self, shop, product):
        """
        Тест для проверки валидации количества.

        Ожидаемый результат: возникает исключение ValidationError при отрицательном количестве.
        """
        with pytest.raises(ValidationError):
            product_info = ProductInfo(
                product=product,
                shop=shop,
                description="Test Description",
                quantity=-10,
                price=100.00,
                price_rrc=120.00,
            )
            product_info.clean()

    def test_product_info_str_method(self, shop, product):
        """
        Тест метода __str__ модели ProductInfo.

        Ожидаемый результат: метод возвращает строку "Test Description (Supplier Shop)".
        """
        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            description="Test Description",
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        assert str(product_info) == "Test Description (Supplier Shop)"

    @pytest.mark.django_db
    def test_product_info_super_clean_called(self, shop, product):
        """
        Проверяет, что вызов super().clean() выполняется корректно
        и не вызывает ошибок при валидных данных.

        Ожидаемый результат: метод full_clean() выполняется без ошибок.
        """

        product_info = ProductInfo(
            product=product,
            shop=shop,
            quantity=10,
            price=Decimal("100.50"),
            price_rrc=Decimal("120.00"),
        )

        product_info.full_clean()
        assert True
