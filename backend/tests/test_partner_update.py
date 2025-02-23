import json
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model


class PartnerUpdateViewTests(APITestCase):
    def setUp(self):
        """
        Инициализация клиента перед каждым тестом.
        """
        self.client = APIClient()
        self.user = self.create_supplier_user()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("partner-update")

    def create_supplier_user(self):
        """
        Создает пользователя с ролью supplier.
        """
        data = {
            "email": "supplier@example.com",
            "password": "strongpassword123",
            "first_name": "Supplier",
            "last_name": "User",
            "role": "supplier",
        }

        url = reverse("user-register")
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        user = get_user_model().objects.get(email="supplier@example.com")
        assert user is not None
        assert user.role == "supplier"

        return user

    def load_json_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_upload_json_file(self):
        json_file_path = os.path.join("data", "shop1.json")
        test_data = self.load_json_file(json_file_path)

        json_file = SimpleUploadedFile(
            "shop1.json",
            json.dumps(test_data, ensure_ascii=False).encode("utf-8"),
            content_type="application/json",
        )

        response = self.client.post(self.url, {"file": json_file}, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert (
            "Задача на загрузку данных поставлена в очередь" in response.data["message"]
        )

    def test_upload_invalid_file_format(self):
        text_file = SimpleUploadedFile(
            "shop1.txt", b"Some text data", content_type="text/plain"
        )

        response = self.client.post(self.url, {"file": text_file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверный формат файла. Ожидается JSON." in response.data["error"]

    def test_upload_no_file(self):
        response = self.client.post(self.url, {}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No file was submitted." in response.data["file"]
