from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator


class User(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя')
    email = models.EmailField(max_length=200, unique=True, verbose_name='Email', db_index=True)
    password = models.CharField(max_length=200, verbose_name='Пароль', validators=[MinLengthValidator(8)])

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('-email',)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Shop(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название', unique=True, db_index=True)
    url = models.URLField(max_length=200, null=True, blank=True, verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True, verbose_name='Магазины')
    name = models.CharField(max_length=200, verbose_name='Название', db_index=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    model = models.CharField(max_length=255, verbose_name='Модель', blank=True)
    name = models.CharField(max_length=80, verbose_name='Название', db_index=True)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True, verbose_name='Описание')
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Список информации о продуктах"
        ordering = ('-description',)
        unique_together = ('product', 'shop')

    def __str__(self):
        return f"{self.description} ({self.shop.name})"


class Parameter(models.Model):
    name = models.CharField(max_length=200, verbose_name='Параметр', db_index=True)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters',
                                  on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=200)

    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = "Список параметров продукта"
        ordering = ('-parameter',)

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='orders')
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    status = models.CharField(max_length=20, verbose_name='Статус', choices=STATUS_CHOICES, default='new')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-dt',)

    def __str__(self):
        return f"Заказ номер {self.id} - {self.get_status_display()}"

    def total_cost(self):
        return sum(item.cost() for item in self.order_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = "Список позиций заказа"
        ordering = ('-order',)

    def __str__(self):
        return f"{self.product.name} : {self.quantity}"

    def cost(self):
        product_info = self.product.product_infos.filter(shop=self.shop).first()
        if product_info:
            return self.quantity * product_info.price
        return 0


class Contact(models.Model):
    CONTACT_TYPES = [
        ('phone', 'Телефон'),
        ('email', 'Email'),
        ('address', 'Адрес'),
    ]

    type = models.CharField(max_length=20, verbose_name='Тип', choices=CONTACT_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='contacts')
    value = models.CharField(max_length=100, verbose_name='Значение')
    city = models.CharField(max_length=50, verbose_name='Город', default='Unknown')
    street = models.CharField(max_length=100, verbose_name='Улица', default='Unknown')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', default='Unknown',
                             validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = "Список контактов"
        ordering = ('-type',)

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'