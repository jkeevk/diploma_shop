from django.db import models

class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('-email',)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Shop(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name

class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.FloatField()
    price_rrc = models.FloatField()

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Список информации о продуктах"
        ordering = ('-name',)

    def __str__(self):
        return f"{self.name} ({self.shop.name})"

class Parameter(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters', blank=True,
                                     on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=200)

    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = "Список параметров"
        ordering = ('-parameter',)

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-dt',)

    def __str__(self):
        return f"Заказ номер {self.id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = "Список позиций заказа"
        ordering = ('-order',)
    
    def __str__(self):
        return f"{self.product.name} : {self.quantity}"
    
class Contact(models.Model):
    type = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    value = models.CharField(max_length=100)
    city = models.CharField(max_length=50, verbose_name='Город', default='Unknown')
    street = models.CharField(max_length=100, verbose_name='Улица', default='Unknown')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', default='Unknown')



    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = "Список контактов"
        ordering = ('-type',)

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'