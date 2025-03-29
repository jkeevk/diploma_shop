from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Создание суперпользователя"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email", required=True, help="Почта для суперпользователя"
        )
        parser.add_argument(
            "--password", required=True, help="Пароль для суперпользователя"
        )
        parser.add_argument("--role", required=True, help="Роль для суперпользователя")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        role = options["role"]

        User.objects.filter(email=email).delete()
        User.objects.create_superuser(email=email, password=password, role=role)
        self.stdout.write(self.style.SUCCESS("Суперпользователь успешно создан"))
