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
    Тестирование метода save_model в UserAdmin для создания и обновления пользователей.
    """

    def test_create_user_with_valid_password(self, user_admin):
        """Тест: создание нового пользователя с паролем.

        Ожидаемый результат:
        - Пароль пользователя правильно зашифрован.
        - Данные пользователя сохранены корректно.
        """
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

    def test_update_user_password_with_change(self, user_admin, sample_user):
        """Тест: обновление пользователя с изменением пароля.

        Ожидаемый результат:
        - Пароль пользователя обновляется.
        - Другие данные остаются неизменными.
        """
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
        """Тест: обновление пользователя без изменения пароля.

        Ожидаемый результат:
        - Данные пользователя обновляются, но пароль остается прежним.
        """
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

    def test_create_user_without_password(self, user_admin):
        """Тест: создание пользователя без пароля.

        Ожидаемый результат:
        - Пароль остается пустым.
        - Данные пользователя сохраняются корректно.
        """
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

    def test_super_method_is_called_on_user_update(
        self, user_admin, sample_user, mocker
    ):
        """Тест: вызов родительского метода save_model при обновлении пользователя.

        Ожидаемый результат:
        - Родительский метод save_model должен быть вызван.
        """
        form = forms.Form()
        form.cleaned_data = {"email": sample_user.email, "first_name": "Test"}

        request = None
        mock_super = mocker.patch("django.contrib.admin.ModelAdmin.save_model")

        user_admin.save_model(request, sample_user, form, change=True)

        mock_super.assert_called_once_with(request, sample_user, form, True)


@pytest.mark.django_db
class TestProductParameterAdmin:
    """
    Тестирование методов в ProductParameterAdmin для работы с параметрами продуктов.
    """

    def test_product_info_formatting(self, product_parameter_admin, product_parameter):
        """Тест: корректное форматирование информации о продукте.

        Ожидаемый результат:
        - Метод product_info корректно форматирует строку.
        """
        actual_output = product_parameter_admin.product_info(product_parameter)
        assert actual_output == "Test Product (Supplier Shop)"


@pytest.mark.django_db
class TestOrderAdmin:
    """
    Тестирование методов в OrderAdmin для работы с заказами.
    """

    def test_order_total_cost_calculation(self, order_admin, order):
        """Тест: правильное вычисление общей стоимости заказа.

        Ожидаемый результат:
        - Метод total_cost корректно вычисляет общую стоимость заказа.
        """
        actual_output = order_admin.total_cost(order)
        assert actual_output == 100 * 2


@pytest.mark.django_db
class TestOrderItemAdmin:
    """
    Тестирование методов в OrderItemAdmin для работы с элементами заказов.
    """

    def test_item_cost_calculation(self, order_item_admin, order_item):
        """Тест: правильное вычисление стоимости элемента заказа.

        Ожидаемый результат:
        - Метод cost корректно вычисляет стоимость элемента заказа.
        """
        actual_output = order_item_admin.cost(order_item)
        assert actual_output == 100 * 3

    def test_check_role_permission_for_safe_methods(self):
        """Тест: разрешение для безопасных методов при allow_safe_methods_for_all=True.

        Ожидаемый результат:
        - Разрешение возвращает True для безопасных методов, независимо от роли пользователя.
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
    Тестирование методов в PriceUpdateAdmin для обновления цен товаров.
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
        """Полная очистка всех кэшей и хранилищ."""
        cache.clear()
        self.redis_conn.flushdb()

    def test_get_request_renders_correct_template(self):
        """Тест: GET-запрос должен отображать правильный шаблон.

        Ожидаемый результат:
        - Статус ответа 200.
        - Используется шаблон 'admin/price_update.html'.
        """
        response = self.client.get(reverse("admin:price_update"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/price_update.html")
        self.assertContains(response, "Обновление прайс-листа")

    def test_post_request_without_file_shows_error_message(self):
        """Тест: POST-запрос без файла должен вывести ошибку.

        Ожидаемый результат:
        - Появляется сообщение об ошибке "Файл не выбран!".
        """
        response = self.client.post(reverse("admin:price_update"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Файл не выбран!")

    def test_post_request_with_invalid_file_shows_error_message(self):
        """Тест: POST-запрос с файлом неправильного формата должен вывести ошибку.

        Ожидаемый результат:
        - Появляется сообщение об ошибке "Требуется JSON-файл!".
        """
        file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        response = self.client.post(reverse("admin:price_update"), {"file": file})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Требуется JSON-файл!")

    @patch("backend.admin.default_storage.save")
    @patch("backend.admin.export_products_task.delay")
    def test_valid_file_triggers_data_processing(self, mock_task, mock_save):
        """Тест: POST-запрос с правильным файлом должен запускать обработку данных.

        Ожидаемый результат:
        - Файл сохраняется в хранилище.
        - Задача на обработку данных запускается.
        """
        file = SimpleUploadedFile("test.json", b"{}", content_type="application/json")
        response = self.client.post(reverse("admin:price_update"), {"file": file})

        expected_path = os.path.join("data", "test.json")
        mock_save.assert_called_once_with(expected_path, ANY)
        mock_task.assert_called_once_with(expected_path)

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Файл принят в обработку", str(messages[0]))

    @patch("backend.admin.default_storage.save", side_effect=Exception("Test error"))
    def test_file_save_error_handling(self, mock_save):
        """Тест: обработка ошибок при сохранении файла.

        Ожидаемый результат:
        - Появляется сообщение об ошибке при сохранении файла.
        """
        file = SimpleUploadedFile("test.json", b"{}", content_type="application/json")
        response = self.client.post(reverse("admin:price_update"), {"file": file})

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Ошибка: Test error", str(messages[0]))
