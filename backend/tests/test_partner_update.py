import json
import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPartnerUpdateView:
    """Набор тестов для обновления данных партнера через загрузку файлов."""

    @pytest.fixture
    def partner_update_url(self):
        """URL для обновления данных партнера."""
        return reverse("partner-update")

    def load_test_json(self, filename):
        """Загружает тестовый JSON файл из директории data."""
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    def test_supplier_can_upload_valid_json_file(
        self, api_client, partner_update_url, supplier
    ):
        """
        Тест: Продавец может загрузить валидный JSON файл.
        Проверки:
        - Статус 200 OK
        - Корректное сообщение об успешной постановке задачи
        - Файл передается в правильном формате
        """
        # Подготовка тестовых данных
        test_file_path = os.path.join("data", "shop1.json")
        json_data = self.load_test_json(test_file_path)

        test_file = SimpleUploadedFile(
            name="shop1.json",
            content=json.dumps(json_data, ensure_ascii=False).encode("utf-8"),
            content_type="application/json",
        )

        # Выполнение запроса
        api_client.force_authenticate(user=supplier)
        response = api_client.post(
            partner_update_url, {"file": test_file}, format="multipart"
        )

        # Проверки
        assert response.status_code == status.HTTP_200_OK
        assert (
            "Задача на загрузку данных поставлена в очередь" in response.data["message"]
        )

    def test_upload_rejects_non_json_files(
        self, api_client, partner_update_url, supplier
    ):
        """
        Тест: Система отклоняет файлы с неправильным форматом.
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение о неверном формате файла
        """
        # Подготовка тестовых данных
        invalid_file = SimpleUploadedFile(
            name="invalid.txt", content=b"Plain text content", content_type="text/plain"
        )

        # Выполнение запроса
        api_client.force_authenticate(user=supplier)
        response = api_client.post(
            partner_update_url, {"file": invalid_file}, format="multipart"
        )

        # Проверки
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверный формат файла. Ожидается JSON." in response.data["error"]

    def test_upload_without_file_returns_error(
        self, api_client, partner_update_url, supplier
    ):
        """
        Тест: Попытка загрузки без файла возвращает ошибку.
        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение об отсутствии файла
        """
        # Выполнение запроса
        api_client.force_authenticate(user=supplier)
        response = api_client.post(partner_update_url, {}, format="multipart")

        # Проверки
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No file was submitted" in str(response.data["file"])

    def test_server_error_handling_during_upload(
        self, api_client, partner_update_url, supplier, mocker
    ):
        """
        Тест: Обработка внутренней ошибки сервера при загрузке.
        Ожидаемый результат:
        - Статус 500 Internal Server Error
        - Сообщение об ошибке с деталями
        """
        # Мокирование ошибки
        mocker.patch("builtins.open", side_effect=Exception("Test error"))

        # Подготовка тестовых данных
        test_file = SimpleUploadedFile(
            name="test.json",
            content=b'{"key": "value"}',
            content_type="application/json",
        )

        # Выполнение запроса
        api_client.force_authenticate(user=supplier)
        response = api_client.post(
            partner_update_url, {"file": test_file}, format="multipart"
        )

        # Проверки
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Ошибка при загрузке файла: Test error" in response.data["error"]
