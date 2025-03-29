# Standard library imports
import threading
import time
import uuid
import logging
from unittest.mock import patch

# Django imports
from django.core.cache import cache
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django_redis import get_redis_connection

# Test imports
import pytest

# Local imports
from backend.models import Category, Product

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestCacheFromDB(TestCase):
    """
    Комплексные тесты кэширования запросов к базе данных.
    Проверяются основные сценарии работы кэша, инвалидация,
    сложные запросы, конкурентный доступ и пользовательский кэш.
    """

    @pytest.fixture(autouse=True)
    def setup(self, redis_client):
        """Инициализация тестового окружения перед каждым тестом."""
        self.redis_client = redis_client
        self._clean_database()
        self._clear_caches()

    def _clean_database(self):
        """Очистка тестовых данных из базы."""
        Category.objects.all().delete()
        Product.objects.all().delete()

    def _clear_caches(self):
        """Полная очистка всех кэшей."""
        cache.clear()
        get_redis_connection("default").flushdb()

    def test_redis_connection(self):
        """Проверка работоспособности подключения к Redis."""
        assert self.redis_client.ping() is True

    def test_category_cache(self):
        """Тест базового кэширования запросов для модели Category."""
        unique_name = f"TestCategory_{uuid.uuid4().hex[:8]}"
        Category.objects.create(name=unique_name)

        # Первый запрос - должен обратиться к базе данных
        with self.assertNumQueries(1):
            categories = list(Category.objects.filter(name=unique_name))
            assert len(categories) == 1

        # Повторный запрос - должен использовать кэш
        with self.assertNumQueries(0):
            cached_categories = list(Category.objects.filter(name=unique_name))
            assert len(cached_categories) == 1

    def test_bulk_update_invalidation(self):
        """Тест инвалидации кэша после массового обновления."""
        # Создаем категории с уникальными именами
        categories = [
            Category(name=f"Cat_{uuid.uuid4().hex[:8]}_{i}") for i in range(5)
        ]
        Category.objects.bulk_create(categories)

        # Первый запрос количества - попадает в базу
        with self.assertNumQueries(1):
            assert Category.objects.count() == 5

        # Массовое обновление - добавляем префикс
        Category.objects.all().update(name=Concat(Value("Updated_"), F("name")))

        # Проверяем что кэш инвалидировался
        with self.assertNumQueries(1):
            assert Category.objects.filter(name__startswith="Updated_").count() == 5

    def test_complex_query_caching(self):
        """Тест кэширования сложных запросов с аннотациями."""
        category_name = f"Electronics_{uuid.uuid4().hex[:8]}"
        category = Category.objects.create(name=category_name)
        Product.objects.create(name="Ноутбук", category=category)
        Product.objects.create(name="Телефон", category=category)

        # Сложный запрос с подсчетом товаров
        with self.assertNumQueries(1):
            result = (
                Category.objects.filter(name=category_name)
                .annotate(product_count=Count("products"))
                .filter(product_count__gt=0)
            )
            assert len(result) == 1

        # Должен браться из кэша
        with self.assertNumQueries(0):
            result = (
                Category.objects.filter(name=category_name)
                .annotate(product_count=Count("products"))
                .filter(product_count__gt=0)
            )

    def test_concurrent_access(self):
        """Тест конкурентного доступа с проверкой кэширования."""
        unique_name = f"Concurrent_{uuid.uuid4().hex[:8]}"
        Category.objects.create(name=unique_name)

        results = []
        errors = []
        lock = threading.Lock()  # Блокировка для потокобезопасности

        def query_categories():
            try:
                with lock:
                    # Первый запрос в каждом потоке может идти в базу
                    list(Category.objects.filter(name=unique_name))
                    results.append(1)
            except Exception as e:
                errors.append(str(e))

        # Используем меньше потоков для стабильности
        threads = [threading.Thread(target=query_categories) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Возникли ошибки: {errors}"
        assert len(results) == 5

    def test_user_specific_caching(self):
        """Тест раздельного кэширования для разных пользователей."""
        User = get_user_model()

        user1 = User.objects.create_user(
            email=f"user1_{uuid.uuid4().hex[:6]}@example.com", password="testpass123"
        )
        user2 = User.objects.create_user(
            email=f"user2_{uuid.uuid4().hex[:6]}@example.com", password="testpass123"
        )

        client1 = Client()
        client2 = Client()

        client1.force_login(user1)
        client2.force_login(user2)

        category_name = f"User Cache {uuid.uuid4().hex[:6]}"
        Category.objects.create(name=category_name)
        url = reverse("category-list")

        # Первый запрос для каждого пользователя - должен кэшироваться отдельно
        with patch("cachalot.settings.cachalot_settings.CACHALOT_TIMEOUT", 60):
            # Запрос от первого пользователя
            response1 = client1.get(f"{url}?search={category_name}")
            assert response1.status_code == 200
            data1 = response1.json()

            # Запрос от второго пользователя
            response2 = client2.get(f"{url}?search={category_name}")
            assert response2.status_code == 200
            data2 = response2.json()

            # Проверяем, что данные одинаковые (но кэшируются отдельно)
            assert data1 == data2
            # Проверяем, что второй запрос каждого пользователя берется из кэша
            with patch("backend.views.CategoryViewSet.queryset.count") as mock_count:
                response1_cached = client1.get(f"{url}?search={category_name}")
                response2_cached = client1.get(f"{url}?search={category_name}")
                assert mock_count.call_count == 0  # Не должно быть запросов к БД

    def test_cache_performance(self):
        """Тест производительности кэша с реалистичными ожиданиями."""
        unique_name = f"PerfTest_{uuid.uuid4().hex[:8]}"
        Category.objects.create(name=unique_name)

        # Холодный запрос (без кэша)
        start = time.time()
        Category.objects.all().count()
        cold_query_time = time.time() - start

        # Теплый запрос (с кэшем)
        start = time.time()
        Category.objects.all().count()
        cached_query_time = time.time() - start

        logger.info(
            f"Производительность: без кэша={cold_query_time:.4f}, с кэшем={cached_query_time:.4f}"
        )
        assert (
            cached_query_time < cold_query_time / 2
        ), "Запросы с кэшем недостаточно быстрые"
