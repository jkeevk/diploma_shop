import json
import os
from django.core.management.base import BaseCommand
from backend.models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
)


class Command(BaseCommand):
    """
    Команда для загрузки или обновления данных о товарах в базу данных из JSON файла.

    Файл JSON должен содержать информацию о магазине, категориях товаров и самих товарах.
    Эта команда анализирует файл, извлекает необходимые данные и обновляет или создает записи в базе данных.

    Аргументы:
        json_file (str): Путь к файлу JSON с данными о товарах
    """

    help = "Загружает или обновляет данные о товарах из JSON файла в базу данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Путь к файлу JSON с данными о товарах"
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"Файл {json_file} не найден."))
            return

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                products_data = json.load(f)
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(f"Файл {json_file} содержит некорректный JSON.")
            )
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при чтении файла: {e}"))
            return

        try:
            shop_data = products_data[0].get("shop")
            categories_data = products_data[1].get("categories")
            goods_data = products_data[2].get("goods")
        except (IndexError, AttributeError):
            self.stdout.write(self.style.ERROR("Некорректная структура JSON файла."))
            return

        if not shop_data or not categories_data or not goods_data:
            self.stdout.write(
                self.style.ERROR("Отсутствуют необходимые данные в JSON.")
            )
            return

        shop, created = Shop.objects.get_or_create(name=shop_data)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Создан магазин '{shop.name}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Найден магазин '{shop.name}'"))

        categories = {}
        for category_data in categories_data:
            try:
                category, created = Category.objects.get_or_create(
                    name=category_data["name"]
                )
                categories[category_data["id"]] = category
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Создана категория '{category.name}'")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"Найдена категория '{category.name}'")
                    )
            except KeyError:
                self.stdout.write(
                    self.style.ERROR(
                        f"Отсутствует поле 'name' в данных категории: {category_data}"
                    )
                )
                continue

        for good_data in goods_data:
            try:
                product_name = good_data["name"]
                category_id = good_data["category"]
                product_model = good_data.get("model", "")
                description = good_data.get("description", "")
                external_id = good_data.get("id")
            except KeyError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Отсутствует обязательное поле {e} в данных товара: {good_data}"
                    )
                )
                continue

            category = categories.get(category_id)
            if not category:
                self.stdout.write(
                    self.style.ERROR(
                        f"Категория с ID {category_id} не найдена для товара '{product_name}'."
                    )
                )
                continue

            product, created = Product.objects.update_or_create(
                name=product_name,
                defaults={"category": category, "model": product_model},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан товар '{product_name}'"))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Обновлен товар '{product_name}'")
                )

            try:
                product_info = ProductInfo.objects.filter(
                    product=product, shop=shop
                ).first()

                if product_info:
                    product_info.external_id = external_id
                    product_info.description = description
                    product_info.quantity = good_data.get("quantity", 0)
                    product_info.price = good_data["price"]
                    product_info.price_rrc = good_data["price_rrc"]
                    product_info.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Обновлена информация о товаре '{product_name}' в магазине '{shop.name}'"
                        )
                    )
                else:
                    product_info = ProductInfo.objects.create(
                        product=product,
                        shop=shop,
                        external_id=external_id,
                        description=description,
                        quantity=good_data.get("quantity", 0),
                        price=good_data["price"],
                        price_rrc=good_data["price_rrc"],
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Создана информация о товаре '{product_name}' в магазине '{shop.name}'"
                        )
                    )
            except KeyError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Отсутствует обязательное поле {e} в данных товара: {good_data}"
                    )
                )
                continue

            parameters_data = good_data.get("parameters", {})
            if product_info:
                for param_name, param_value in parameters_data.items():
                    try:
                        parameter, created = Parameter.objects.update_or_create(
                            name=param_name,
                            defaults={},
                        )

                        ProductParameter.objects.update_or_create(
                            product_info=product_info,
                            parameter=parameter,
                            defaults={"value": param_value},
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Ошибка при обработке параметра '{param_name}': {e}"
                            )
                        )
                        continue
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Информация о товаре '{product_name}' в магазине '{shop.name}' не найдена. Пропуск параметров."
                    )
                )
        self.stdout.write(
            self.style.SUCCESS("Данные успешно загружены или обновлены в базе данных.")
        )
