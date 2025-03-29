import json
import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPartnerUpdateView:
    """
    Тесты для представления PartnerUpdateView.
    """

    @pytest.fixture
    def url(self):
        """Фикстура для получения URL представления."""
        return reverse("partner-update")

    def load_json_file(self, filename):
        """Загружает JSON-файл."""
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_upload_json_file(self, api_client, url, supplier):
        """
        Тест успешной загрузки JSON-файла.
        """
        api_client.force_authenticate(user=supplier)

        json_file_path = os.path.join("data", "shop1.json")
        test_data = self.load_json_file(json_file_path)

        json_file = SimpleUploadedFile(
            "shop1.json",
            json.dumps(test_data, ensure_ascii=False).encode("utf-8"),
            content_type="application/json",
        )

        response = api_client.post(url, {"file": json_file}, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert (
            "Задача на загрузку данных поставлена в очередь" in response.data["message"]
        )

    def test_upload_invalid_file_format(self, api_client, url, supplier):
        """
        Тест загрузки файла с неверным форматом.
        """
        api_client.force_authenticate(user=supplier)

        text_file = SimpleUploadedFile(
            "shop1.txt", b"Some text data", content_type="text/plain"
        )

        response = api_client.post(url, {"file": text_file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверный формат файла. Ожидается JSON." in response.data["error"]

    def test_upload_no_file(self, api_client, url, supplier):
        """
        Тест загрузки без файла.
        """
        api_client.force_authenticate(user=supplier)

        response = api_client.post(url, {}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No file was submitted." in response.data["file"]

    def test_upload_file_processing_error(self, api_client, url, supplier, mocker):
        """
        Проверяем обработку внутренней ошибки сервера при загрузке файла.
        """
        api_client.force_authenticate(user=supplier)

        json_file = SimpleUploadedFile(
            "test.json",
            b'{"key": "value"}',
            content_type="application/json",
        )

        mocker.patch("builtins.open", side_effect=Exception("Test error"))

        response = api_client.post(url, {"file": json_file}, format="multipart")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Ошибка при загрузке файла: Test error" in response.data["error"]
