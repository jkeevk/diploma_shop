import os
from unittest.mock import patch, ANY

import pytest
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from backend.permissions import CheckRole
from django_redis import get_redis_connection


User = get_user_model()


@pytest.mark.django_db
class TestUserAdminSaveModel:
    """
    Класс для тестирования метода save_model в UserAdmin.
    """

    def test_create_new_user(self, user_admin):
        """Тест создания нового пользователя с паролем"""
        form = forms.Form()
        form.cleaned_data = {
            "password1": "new_secure_password",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
        }

        user = User(email="new@example.com")
        request = None

        user_admin.save_model(request, user, form, change=False)

        assert user.check_password("new_secure_password")
        assert user.email == "new@example.com"

    def test_update_user_with_password_change(self, user_admin, sample_user):
        """Тест обновления пользователя с изменением пароля"""
        form = forms.Form()
        form.cleaned_data = {
            "password": "changed_password",
            "email": sample_user.email,
            "first_name": sample_user.first_name,
            "last_name": sample_user.last_name,
        }

        request = None

        user_admin.save_model(request, sample_user, form, change=True)

        assert sample_user.check_password("changed_password")
        assert sample_user.first_name == "John"

    def test_update_user_without_password_change(self, user_admin, sample_user):
        """Тест обновления пользователя без изменения пароля"""
        hashed_password = sample_user.password
        form = forms.Form()
        form.cleaned_data = {
            "email": sample_user.email,
            "first_name": "Martin",
            "last_name": sample_user.last_name,
        }

        request = None

        user_admin.save_model(request, sample_user, form, change=True)

        sample_user.refresh_from_db()

        assert sample_user.first_name == "Martin"
        assert sample_user.password == hashed_password

    def test_create_user_with_empty_password(self, user_admin):
        """Тест создания пользователя без пароля"""
        form = forms.Form()
        form.cleaned_data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
        }

        user = User(email="new@example.com")
        request = None

        user_admin.save_model(request, user, form, change=False)

        assert user.email == "new@example.com"
        assert user.password == ""

    def test_super_method_called(self, user_admin, sample_user, mocker):
        """Тест вызова родительского метода save_model"""
        form = forms.Form()
        form.cleaned_data = {"email": sample_user.email, "first_name": "Test"}

        request = None
        mock_super = mocker.patch("django.contrib.admin.ModelAdmin.save_model")

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
        assert actual_output == 100 * 2


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
        assert actual_output == 100 * 3

    def test_check_role_allow_safe_methods_for_all(self):
        """
        Проверяет, что при allow_safe_methods_for_all=True и безопасном методе запроса
        разрешение возвращает True независимо от роли пользователя.
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            role="any_role",
            is_active=True,
        )

        permission = CheckRole(
            "required_role1", "required_role2", allow_safe_methods_for_all=True
        )

        factory = APIRequestFactory()
        request = factory.get("/some-url/")
        request.user = user

        assert permission.has_permission(request, None) is True


@pytest.mark.django_db
class TestPriceUpdateAdmin(TestCase):
    """
    Тесты для PriceUpdateAdmin (админка для обновления товаров от поставщиков)
    """

    @classmethod
    def setUpClass(cls):
        """Инициализация подключения к Redis перед всеми тестами."""
        super().setUpClass()
        cls.redis_conn = get_redis_connection("default")

    def setUp(self):
        """Инициализация тестового окружения перед каждым тестом."""

        self._clear_caches()
        self.admin_user = User.objects.create_superuser(
            email="admin_test@example.com", password="password21", is_staff=True
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def tearDown(self):
        """Очистка тестового окружения после каждого теста."""

        self._clear_caches()

    def _clear_caches(self):
        """Полная очистка всех кэшей и хранилищ"""

        cache.clear()
        self.redis_conn.flushdb()

    def test_get_request_renders_template(self):
        """Тестирует, что GET-запрос отображает шаблон."""

        response = self.client.get(reverse("admin:price_update"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/price_update.html")
        self.assertContains(response, "Обновление прайс-листа")

    def test_post_without_file_shows_error(self):
        """Тестирует, что POST-запрос без файла отображает ошибку."""

        response = self.client.post(reverse("admin:price_update"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Файл не выбран!")

    def test_post_with_non_json_file_shows_error(self):
        """Тестирует, что POST-запрос с файлом неверного формата отображает ошибку."""

        file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        response = self.client.post(reverse("admin:price_update"), {"file": file})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Требуется JSON-файл!")

    @patch("backend.admin.default_storage.save")
    @patch("backend.admin.export_products_task.delay")
    def test_valid_file_triggers_processing(self, mock_task, mock_save):
        """Тестирует, что POST-запрос с правильным файлом запускает обработку данных."""

        file = SimpleUploadedFile("test.json", b"{}", content_type="application/json")
        response = self.client.post(reverse("admin:price_update"), {"file": file})

        expected_path = os.path.join("data", "test.json")
        mock_save.assert_called_once_with(expected_path, ANY)
        mock_task.assert_called_once_with(expected_path)

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Файл принят в обработку", str(messages[0]))

    @patch("backend.admin.default_storage.save", side_effect=Exception("Test error"))
    def test_file_save_error_handling(self, mock_save):
        """Тестирует обработку ошибок при сохранении файла."""

        file = SimpleUploadedFile("test.json", b"{}", content_type="application/json")
        response = self.client.post(reverse("admin:price_update"), {"file": file})

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Ошибка: Test error", str(messages[0]))
