import pytest
from backend.models import Product, Category

@pytest.mark.django_db
class TestProductModel:
    """
    Тесты для модели Product.
    """
    def setup_method(self):
        """
        Инициализация объектов перед каждым тестом.
        """
        self.category = Category.objects.create(
            name="Test Category",
        )
        self.product = Product.objects.create(
            name="Test Product",
            model="Test Model",
            category=self.category,
        )

    def test_create_product(self):
        """
        Тест создания товара.
        """
        product = Product.objects.create(
            name="Another Test Product",
            model="Another Test Model",
            category=self.category,
        )
        assert product.name == "Another Test Product"
        assert product.model == "Another Test Model"
        assert product.category == self.category

    def test_read_product(self):
        """
        Тест получения информации о товаре.
        """
        product = self.product
        assert product.name == "Test Product"
        assert product.model == "Test Model"
        assert product.category == self.category

    def test_update_product(self):
        """
        Тест обновления товара.
        """
        product = self.product
        product.name = "Updated Product"
        product.model = "Updated Model"
        product.save()

        updated_product = Product.objects.get(id=product.id)
        assert updated_product.name == "Updated Product"
        assert updated_product.model == "Updated Model"

    def test_delete_product(self):
        """
        Тест удаления товара.
        """
        product_id = self.product.id
        self.product.delete()
        assert not Product.objects.filter(id=product_id).exists()
