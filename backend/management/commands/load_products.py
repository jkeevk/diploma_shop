import json
import os
from django.core.management.base import BaseCommand
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

class Command(BaseCommand):
    """
    Команда для загрузки или обновления данных о товарах в базу данных из JSON файла.
    
    Файл JSON должен содержать информацию о магазине, категориях товаров и самих товарах.
    Эта команда анализирует файл, извлекает необходимые данные и обновляет или создает записи в базе данных.
    
    Аргументы:
        json_file (str): Путь к JSON файлу, содержащему данные о товарах, магазинах и категориях.
    """
    help = 'Загружает или обновляет данные о товарах из JSON файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь к файлу JSON с данными о товарах')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        # Проверяем наличие файла
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"Файл {json_file} не найден."))
            return

        # Открываем и загружаем данные из файла
        with open(json_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        # Извлекаем данные о магазине, категориях и товарах
        shop_data = products_data[0].get('shop')
        categories_data = products_data[1].get('categories')
        goods_data = products_data[2].get('goods')

        # Проверка на наличие всех обязательных данных
        if not shop_data or not categories_data or not goods_data:
            self.stdout.write(self.style.ERROR('Отсутствуют необходимые данные в JSON.'))
            return

        # Обрабатываем магазин
        shop, created = Shop.objects.get_or_create(name=shop_data)

        # Обрабатываем категории
        categories = {}
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(name=category_data['name'])
            categories[category_data['id']] = category

        # Обрабатываем товары
        for good_data in goods_data:
            product_name = good_data.get('name')
            category_id = good_data.get('category')

            # Проверка на наличие категории
            category = categories.get(category_id)
            if not category:
                self.stdout.write(self.style.ERROR(f"Категория с ID {category_id} не найдена для товара {product_name}."))
                continue

            # Обновляем или создаем продукт
            product, created = Product.objects.update_or_create(
                name=product_name,
                defaults={'category': category}
            )

            # Логируем успешное создание или обновление товара
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан товар '{product_name}'"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Обновлен товар '{product_name}'"))

            # Создаем или обновляем информацию о продукте в магазине
            product_info, created = ProductInfo.objects.update_or_create(
                product=product,
                shop=shop,
                defaults={
                    'name': good_data['name'],
                    'quantity': good_data['quantity'],
                    'price': good_data['price'],
                    'price_rrc': good_data['price_rrc']
                }
            )

            # Логируем информацию о продукте
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создана информация о товаре '{product_name}' в магазине '{shop.name}'"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Обновлена информация о товаре '{product_name}' в магазине '{shop.name}'"))

            # Обрабатываем параметры товара
            parameters_data = good_data.get('parameters', {})
            for param_name, param_value in parameters_data.items():
                # Создаем или обновляем параметр
                parameter, created = Parameter.objects.update_or_create(
                    name=param_name,
                    defaults={}
                )

                # Создаем или обновляем связь параметра с продуктом
                ProductParameter.objects.update_or_create(
                    product_info=product_info,
                    parameter=parameter,
                    defaults={'value': param_value}
                )

        self.stdout.write(self.style.SUCCESS('Данные успешно загружены или обновлены в базе данных.'))
