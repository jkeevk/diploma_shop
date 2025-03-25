import pytest
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django import forms
from backend.admin import UserAdmin, ProductParameterAdmin, OrderAdmin, OrderItemAdmin
from backend.models import User, ProductParameter, Order, OrderItem

User = get_user_model()


@pytest.fixture
def user_admin():
    admin_site = AdminSite()
    return UserAdmin(User, admin_site)


@pytest.fixture
def sample_user():
    return User.objects.create_user(
        email='test@example.com',
        password='initial_password',
        first_name='John',
        last_name='Doe'
    )

@pytest.fixture
def product_parameter_admin(user_admin):
    """Фикстура для создания экземпляра ProductParameterAdmin."""
    return ProductParameterAdmin(ProductParameter, user_admin)

@pytest.fixture
def order_admin(user_admin):
    """Фикстура для создания экземпляра OrderAdmin."""
    return OrderAdmin(Order, user_admin)

@pytest.fixture
def order_item_admin(user_admin):
    """Фикстура для создания экземпляра OrderItemAdmin."""
    return OrderItemAdmin(OrderItem, user_admin)


@pytest.mark.django_db
class TestUserAdminSaveModel:
    """
    Класс для тестирования метода save_model в UserAdmin.
    """
    def test_create_new_user(self, user_admin):
        """Тест создания нового пользователя с паролем"""
        form = forms.Form()
        form.cleaned_data = {
            'password1': 'new_secure_password',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        user = User(email='new@example.com')
        request = None
        
        user_admin.save_model(request, user, form, change=False)
        
        assert user.check_password('new_secure_password')
        assert user.email == 'new@example.com'

    def test_update_user_with_password_change(self, user_admin, sample_user):
        """Тест обновления пользователя с изменением пароля"""
        form = forms.Form()
        form.cleaned_data = {
            'password': 'changed_password',
            'email': sample_user.email,
            'first_name': sample_user.first_name,
            'last_name': sample_user.last_name
        }
        
        request = None
        
        user_admin.save_model(request, sample_user, form, change=True)
        
        assert sample_user.check_password('changed_password')
        assert sample_user.first_name == 'John'

    def test_update_user_without_password_change(self, user_admin, sample_user):
        """Тест обновления пользователя без изменения пароля"""
        hashed_password = sample_user.password
        form = forms.Form()
        form.cleaned_data = {
            'email': sample_user.email,
            'first_name': 'Martin',
            'last_name': sample_user.last_name
        }
        
        request = None
        
        user_admin.save_model(request, sample_user, form, change=True)

        sample_user.refresh_from_db()

        assert sample_user.first_name == 'Martin'
        assert sample_user.password == hashed_password
        
    def test_create_user_with_empty_password(self, user_admin):
        """Тест создания пользователя без пароля"""
        form = forms.Form()
        form.cleaned_data = {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        user = User(email='new@example.com')
        request = None
        
        user_admin.save_model(request, user, form, change=False)
        
        assert user.email == 'new@example.com'
        assert user.password == ''

    def test_super_method_called(self, user_admin, sample_user, mocker):
        """Тест вызова родительского метода save_model"""
        form = forms.Form()
        form.cleaned_data = {
            'email': sample_user.email,
            'first_name': 'Test'
        }
        
        request = None
        mock_super = mocker.patch('django.contrib.admin.ModelAdmin.save_model')
        
        user_admin.save_model(request, sample_user, form, change=True)
        
        mock_super.assert_called_once_with(request, sample_user, form, True)

@pytest.mark.django_db
class TestProductParameterAdmin:
    """
    Тесты для ProductParameterAdmin
    """
    def test_product_info(self, product_parameter_admin, product_parameter):
        """Тестирует метод product_info для правильного форматирования строки."""
        
        actual_output = product_parameter_admin.product_info(product_parameter)        
        assert actual_output == "Test Product (Supplier Shop)"


@pytest.mark.django_db
class TestOrderAdmin:
    """
    Тесты для OrderAdmin
    """
    def test_order_total_cost(self, order_admin, order):
        """Тестирует метод total_cost для правильного вычисления общей стоимости."""
        
        actual_output = order_admin.total_cost(order)
        assert actual_output == 100*2

@pytest.mark.django_db
class TestOrderItemAdmin:
    """
    Тесты для OrderItemAdmin
    """
    def test_item_cost(self, order_item_admin, order_item):
        """
        Тестирует метод cost для правильного вычисления стоимости элемента заказа.
        """
        actual_output = order_item_admin.cost(order_item)
        assert actual_output == 100*3


