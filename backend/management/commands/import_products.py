import json
from django.core.management.base import BaseCommand
from backend.utils.exporters import generate_import_data

class Command(BaseCommand):
    help = "Экспорт данных в JSON-файл"

    def handle(self, *args, **kwargs):
        try:
            data = generate_import_data()
            with open("/app/data/exported_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS("Данные успешно экспортированы"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))