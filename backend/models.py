# Standard library imports
from enum import Enum
from decimal import Decimal

# Django
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify

from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill


class UserRole(Enum):
    """
    Роль пользователя в системе.
    """

    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    ADMIN = "admin"


class UserManager(BaseUserManager):
    """
    Менеджер для управления пользователями. Обеспечивает создание обычных пользователей и суперпользователей.
    """

    def create_user(
        self, email: str, password: str = None, **extra_fields: dict
    ) -> "User":
        """
        Создает и сохраняет пользователя с указанным email и паролем. Если email не указан, выбрасывает исключение.
        """
        if not email:
            raise ValueError("Поле Email должно быть заполнено")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str = None, **extra_fields: dict
    ) -> "User":
        """
        Создает и сохраняет суперпользователя с указанным email и паролем. Убеждается, что is_staff и is_superuser установлены в True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Модель пользователя. Расширяет стандартную модель пользователя Django. Добавляет поля email, role из модели UserRole и confirmation_token.
    """

    email = models.EmailField(unique=True, verbose_name="Email", db_index=True)
    role = models.CharField(
        max_length=30,
        choices=[(role.value, role.name.capitalize()) for role in UserRole],
        default=UserRole.CUSTOMER.value,
        verbose_name="Роль",
    )
    confirmation_token = models.CharField(max_length=255, blank=True, null=True)

    avatar = ProcessedImageField(
        upload_to="avatars/",
        processors=[ResizeToFill(300, 300)],
        format="JPEG",
        options={"quality": 90},
        blank=True,
        null=True,
        verbose_name="Аватарка пользователя",
    )
    avatar_thumbnail = ImageSpecField(
        source="avatar",
        processors=[ResizeToFill(100, 100)],
        format="JPEG",
        options={"quality": 70},
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"
        ordering = ("-email",)

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs) -> None:
        """
        Сохраняет пользователя. Если username не указан, генерирует его на основе email.
        """
        if not self.username:
            self.username = slugify(self.email.replace("@", "_"))

        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Модель категории. Содержит название категории и связь с магазинами.
    """

    shops = models.ManyToManyField(
        "Shop", related_name="categories", blank=True, verbose_name="Магазины"
    )
    name = models.CharField(
        max_length=200, verbose_name="Название", db_index=True, unique=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
        ordering = ("-name",)

    def __str__(self) -> str:
        return self.name


class Contact(models.Model):
    """
    Модель контакта. Содержит информацию о контактах пользователя, включая адрес и телефон.
    """

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="contacts",
    )
    city = models.CharField(max_length=50, verbose_name="Город", blank=True)
    street = models.CharField(max_length=100, verbose_name="Улица", blank=True)
    house = models.CharField(max_length=15, verbose_name="Дом", blank=True)
    structure = models.CharField(max_length=15, verbose_name="Корпус", blank=True)
    building = models.CharField(max_length=15, verbose_name="Строение", blank=True)
    apartment = models.CharField(max_length=15, verbose_name="Квартира", blank=True)
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        blank=True,
        validators=[RegexValidator(regex=r"^\+?1?\d{9,15}$")],
    )

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self) -> str:
        return f"{self.city} {self.street} {self.house}"

    def clean(self) -> None:
        """
        Проверяет, что у пользователя не более 5 контактов. Если больше, выбрасывает исключение.
        """
        if self.user.contacts.count() >= 5:
            raise ValidationError("Максимум 5 адресов на пользователя.")

    def save(self, *args, **kwargs) -> None:
        """
        Сохраняет контакт, предварительно выполняя проверку на количество контактов.
        """
        self.clean()
        super().save(*args, **kwargs)


class Order(models.Model):
    """
    Модель заказа. Содержит информацию о пользователе, дате заказа и его статусе.
    """

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("confirmed", "Подтвержден"),
        ("assembled", "Собран"),
        ("sent", "Отправлен"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    ]

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="orders",
        to_field="id",
    )
    dt = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(
        max_length=20, verbose_name="Статус", choices=STATUS_CHOICES, default="new"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказов"
        ordering = ("-dt",)

    def __str__(self) -> str:
        return f"Заказ номер {self.id} - {self.get_status_display()}"

    def total_cost(self) -> float:
        """
        Возвращает общую стоимость заказа.
        """
        return sum(item.cost() for item in self.order_items.all())

    def clean(self) -> None:
        """
        Проверка на валидность статуса заказа.
        """
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError(
                f"Некорректный статус: {self.status}. Доступные статусы: {', '.join(dict(self.STATUS_CHOICES).keys())}"
            )


class OrderItem(models.Model):
    """
    Модель позиции заказа. Содержит информацию о товаре, магазине и количестве.
    """

    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        verbose_name="Заказ",
        related_name="order_items",
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, verbose_name="Продукт"
    )
    shop = models.ForeignKey("Shop", on_delete=models.CASCADE, verbose_name="Магазин")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Список позиций заказа"
        ordering = ("-order",)

    def __str__(self) -> str:
        return f"{self.product.name} : {self.quantity}"

    def cost(self) -> float:
        """
        Возвращает стоимость позиции заказа.
        """
        product_info = self.product.product_infos.filter(shop=self.shop).first()
        if product_info:
            return self.quantity * product_info.price
        return 0


class Parameter(models.Model):
    """
    Модель параметра. Содержит название параметра.
    """

    name = models.CharField(max_length=200, verbose_name="Параметр", db_index=True)

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        ordering = ("-name",)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """
    Модель товара. Содержит информацию о названии, модели и категории товара.
    """

    model = models.CharField(max_length=255, verbose_name="Модель", blank=True)
    name = models.CharField(max_length=80, verbose_name="Название", db_index=True)
    category = models.ForeignKey(
        "Category",
        verbose_name="Категория",
        related_name="products",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Список товаров"
        ordering = ("-name",)

    def __str__(self) -> str:
        return self.name


class ProductInfo(models.Model):
    """
    Модель информации о товаре. Содержит данные о товаре, магазине, количестве, цене и рекомендуемой розничной цене.
    """

    product = models.ForeignKey(
        "Product",
        verbose_name="Продукт",
        related_name="product_infos",
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        "Shop",
        verbose_name="Магазин",
        related_name="product_infos",
        on_delete=models.CASCADE,
    )
    external_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Внешний ID"
    )
    description = models.CharField(max_length=200, blank=True, verbose_name="Описание")
    quantity = models.PositiveIntegerField(verbose_name="Количество", default=0)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    price_rrc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Рекомендуемая розничная цена",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    image = ProcessedImageField(
        upload_to="products/",
        processors=[ResizeToFill(800, 600)],
        format="JPEG",
        options={"quality": 90},
        blank=True,
        null=True,
        verbose_name="Изображение товара",
    )
    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(300, 200)],
        format="JPEG",
        options={"quality": 80},
    )

    class Meta:
        verbose_name = "Информация о товаре"
        verbose_name_plural = "Список информации о товарах"
        ordering = ("-description",)
        unique_together = ("product", "shop")

    def clean(self) -> None:
        if self.price < 0:
            raise ValidationError("Цена не может быть отрицательной.")
        if self.quantity < 0:
            raise ValidationError("Количество не может быть отрицательным.")
        super().clean()

    def __str__(self) -> str:
        return f"{self.description} ({self.shop.name})"


class ProductParameter(models.Model):
    """
    Модель параметра товара. Содержит информацию о товаре, параметре и его значении.
    """

    product_info = models.ForeignKey(
        "ProductInfo",
        verbose_name="Информация о товаре",
        related_name="product_parameters",
        on_delete=models.CASCADE,
    )
    parameter = models.ForeignKey(
        "Parameter",
        verbose_name="Параметр",
        related_name="product_parameters",
        on_delete=models.CASCADE,
    )
    value = models.CharField(verbose_name="Значение", max_length=200)

    class Meta:
        verbose_name = "Параметр товара"
        verbose_name_plural = "Список параметров товара"
        ordering = ("-parameter",)
        unique_together = ("product_info", "parameter", "value")

    def __str__(self) -> str:
        return f"{self.parameter.name}: {self.value}"


class Shop(models.Model):
    """
    Модель магазина. Содержит информацию о названии магазина, его URL и связанном пользователе.
    """

    name = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ("-name",)

    def __str__(self) -> str:
        return self.name
