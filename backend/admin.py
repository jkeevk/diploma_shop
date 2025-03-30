import os

# Django
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

# Local imports
from .models import (
    Category,
    Contact,
    Order,
    OrderItem,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
    User,
)
from .tasks import export_products_task


class PriceUpdateAdmin(admin.AdminSite):
    """
    Кастомная админка для обновления товаров от поставщиков.
    """

    index_template = "admin/index.html"
    site_header = "Администрирование"

    def has_permission(self, request):
        """
        Проверка доступа к админке.
        """
        return (
            request.user.is_active
            and request.user.is_staff
            and request.user.role in ["admin"]
            and request.user.has_perm("partner.change_price")
        )

    def get_urls(self):
        """
        Добавление дополнительных URL-адресов.
        """
        urls = super().get_urls()
        custom_urls = [
            path("price_update/", self.price_update_view, name="price_update"),
        ]
        return custom_urls + urls

    def price_update_view(self, request):
        """
        Обработка запроса на обновление цен продуктов.
        """
        if request.method == "POST":
            file = request.FILES.get("file")

            if not file:
                messages.error(request, "Файл не выбран!")
                return HttpResponseRedirect(request.path_info)

            if not file.name.endswith(".json"):
                messages.error(request, "Требуется JSON-файл!")
                return HttpResponseRedirect(request.path_info)

            try:
                file_path = os.path.join("data", file.name)
                default_storage.save(file_path, file)
                export_products_task.delay(file_path)
                messages.success(
                    request,
                    "Файл принят в обработку. Обновление может занять несколько минут.",
                )
            except Exception as e:
                messages.error(request, f"Ошибка: {str(e)}")

            return HttpResponseRedirect(request.path_info)

        context = self.each_context(request)
        context.update(
            {"opts": self._registry.keys(), "title": "Обновление прайс-листа"}
        )
        return render(request, "admin/price_update.html", context)


class ProductParameterInline(admin.TabularInline):
    """
    Инлайн интерфейс админки для параметров продукта, связанных с ProductInfo.
    Позволяет добавлять несколько параметров продукта прямо на странице администрирования ProductInfo.
    """

    model = ProductParameter
    extra = 1


class CustomUserChangeForm(UserChangeForm):
    """
    Кастомная форма для редактирования пользователя в админке.
    Добавляет поле для ввода нового пароля с подсказкой и хэширует пароль при его изменении.
    """

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Введите новый пароль"}),
        required=False,
        help_text="Оставьте поле пустым, если не хотите менять пароль.",
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class OrderItemInline(admin.TabularInline):
    """
    Инлайн интерфейс админки для элементов заказов, связанных с заказами.
    Облегчает управление товарами в заказе непосредственно из страницы администрирования заказа.
    """

    model = OrderItem
    extra = 1


class UserAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления пользователями.
    Этот интерфейс предоставляет список пользователей с возможностью поиска и фильтрации по email и роли.
    """

    form = CustomUserChangeForm

    list_display = ("id", "email", "first_name", "last_name", "role", "is_active")
    search_fields = ("id", "email", "first_name", "last_name")
    list_filter = ("role", "is_active")
    ordering = ("-email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "role",
                    "is_active",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """
        Сохраняет пользователя, хэшируя пароль только если он был изменен.
        Если пароль не был изменен, оставляем его без изменений.
        """
        if change:
            if form.cleaned_data.get("password"):
                obj.set_password(form.cleaned_data["password"])
            else:
                obj.password = User.objects.get(pk=obj.pk).password
        else:
            password = form.cleaned_data.get("password1")
            if password:
                obj.set_password(password)
        obj.first_name = form.cleaned_data.get("first_name", obj.first_name)
        obj.last_name = form.cleaned_data.get("last_name", obj.last_name)
        obj.email = form.cleaned_data.get("email", obj.email)
        obj.role = form.cleaned_data.get("role", obj.role)

        super().save_model(request, obj, form, change)


class ShopAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления магазинами.
    Отображает название магазина и URL с возможностью поиска по имени.
    """

    list_display = ("name", "url", "user")
    search_fields = ("name", "user")
    list_filter = ("name",)


class CategoryAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления категориями продуктов.
    Предоставляет возможность поиска по названию категории и управления связанными магазинами.
    """

    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("shops",)


class ProductAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления продуктами.
    Отображает название продукта, категорию и модель с возможностью поиска,
    фильтрации и прямого редактирования в списковом представлении.
    """

    list_display = ("name", "category", "model")
    search_fields = ("name", "model", "category__name")
    list_filter = ("category",)
    list_editable = ("model",)


class ProductInfoAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления информацией о продуктах.
    Отображает данные о продукте, такие как описание, цена и количество,
    с возможностью инлайнового редактирования параметров продукта.
    """

    list_display = ("product", "shop", "description", "price", "quantity", "price_rrc")
    search_fields = ("product__name", "shop__name", "description")
    list_filter = ("product", "shop")
    list_editable = ("description", "price", "quantity", "price_rrc")
    raw_id_fields = ("product", "shop")
    inlines = [ProductParameterInline]


class ParameterAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления параметрами продуктов.
    Отображает названия параметров с возможностью поиска.
    """

    list_display = ("name",)
    search_fields = ("name",)


class ProductParameterAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления параметрами продуктов, связанными с ProductInfo.
    Отображает информацию о продукте, параметре и значении с возможностями поиска и фильтрации.
    """

    list_display = ("product_info", "parameter", "value")
    search_fields = ("value", "parameter__name")
    list_filter = ("parameter",)
    raw_id_fields = ("product_info", "parameter")

    def product_info(self, obj):
        """
        Отображает название продукта и название магазина в сжатом формате.
        """
        return f"{obj.product_info.product.name} ({obj.product_info.shop.name})"

    product_info.short_description = "Информация о продукте"


class OrderAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления заказами.
    Отображает детали заказа, такие как ID, пользователь, статус и общая стоимость с
    возможностями поиска и фильтрации.
    """

    list_display = ("id", "user", "status", "dt", "total_cost")
    search_fields = ("user__email", "status")
    list_filter = ("status",)
    ordering = ("-dt",)
    raw_id_fields = ("user",)
    inlines = [OrderItemInline]

    def total_cost(self, obj):
        """
        Вычисляет и возвращает общую стоимость заказа.
        """
        return obj.total_cost()

    total_cost.short_description = "Общая стоимость"


class OrderItemAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления элементами заказа.
    Отображает детали товаров в заказе, позволяя осуществлять поиск,
    фильтрацию и инлайновое редактирование.
    """

    list_display = ("order", "product", "shop", "quantity", "cost")
    search_fields = ("order__id", "product__name", "shop__name")
    list_filter = ("order",)
    raw_id_fields = ("order", "product", "shop")

    def cost(self, obj):
        """
        Вычисляет и возвращает стоимость элемента заказа.
        """
        return obj.cost()

    cost.short_description = "Стоимость"


class ContactAdmin(admin.ModelAdmin):
    """
    Интерфейс админки для управления контактами пользователей.
    Отображает контактные данные с возможностью редактирования адресов и
    номеров телефонов непосредственно в админке.
    """

    list_display = (
        "id",
        "user",
        "city",
        "street",
        "house",
        "structure",
        "building",
        "apartment",
        "phone",
    )
    search_fields = ("user__email", "city", "street")
    list_filter = ("city",)
    list_editable = ("city", "street", "house")
    raw_id_fields = ("user",)
    fieldsets = (
        (
            "Адрес",
            {
                "fields": (
                    "city",
                    "street",
                    "house",
                    "structure",
                    "building",
                    "apartment",
                    "user",
                )
            },
        ),
        ("Телефон", {"fields": ("phone",)}),
    )


# Регистрация моделей в админке
admin_site = PriceUpdateAdmin(name="myadmin")
admin_site.register(User, UserAdmin)
admin_site.register(Shop, ShopAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(ProductInfo, ProductInfoAdmin)
admin_site.register(Parameter, ParameterAdmin)
admin_site.register(ProductParameter, ProductParameterAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(Contact, ContactAdmin)
admin_site.register(Group, GroupAdmin)
