from django.contrib import admin
from .models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
    Order,
    OrderItem,
    Contact,
)


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "surname", "email")
    search_fields = ("name", "surname", "email")
    list_filter = (
        "name",
        "surname",
    )


class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ("name",)
    list_filter = ("name",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("shops",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "model")
    search_fields = ("name", "model", "category__name")
    list_filter = ("category",)
    list_editable = ("model",)


class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ("product", "shop", "description", "price", "quantity", "price_rrc")
    search_fields = ("product__name", "shop__name", "description")
    list_filter = ("product", "shop")
    list_editable = ("description", "price", "quantity", "price_rrc")
    raw_id_fields = ("product", "shop")
    inlines = [ProductParameterInline]


class ParameterAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ("product_info", "parameter", "value")
    search_fields = ("value", "parameter__name")
    list_filter = ("parameter",)
    raw_id_fields = ("product_info", "parameter")

    def product_info(self, obj):
        return f"{obj.product_info.product.name} ({obj.product_info.shop.name})"

    product_info.short_description = "Product Info"


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "dt", "total_cost")
    search_fields = ("user__name", "status")
    list_filter = ("status",)
    ordering = ("-dt",)
    raw_id_fields = ("user",)
    inlines = [OrderItemInline]

    def total_cost(self, obj):
        return obj.total_cost()

    total_cost.short_description = "Total Cost"


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "shop", "quantity", "cost")
    search_fields = ("order__id", "product__name", "shop__name")
    list_filter = ("order",)
    raw_id_fields = ("order", "product", "shop")

    def cost(self, obj):
        return obj.cost()

    cost.short_description = "Cost"


class ContactAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "street", "house")
    search_fields = ("user__name", "city", "street")
    list_filter = ("phone",)
    list_editable = ("city", "street", "house")
    raw_id_fields = ("user",)
    fieldsets = (
        (
            "Address",
            {
                "fields": (
                    "city",
                    "street",
                    "house",
                    "structure",
                    "building",
                    "apartment",
                )
            },
        ),
        ("Phone", {"fields": ("phone",)}),
    )


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_customer",
        "is_supplier",
        "is_active",
    )
    list_filter = ("is_customer", "is_supplier", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "is_customer", "is_supplier")},
        ),
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
        ("Important dates", {"fields": ("last_login",)}),
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
                    "is_customer",
                    "is_supplier",
                    "is_active",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if obj.password:
            obj.set_password(obj.password)
        obj.created_by_admin = True
        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Contact, ContactAdmin)
