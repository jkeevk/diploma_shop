from django.contrib import admin
from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact
from django.contrib.auth.admin import UserAdmin

class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')
    list_filter = ('name',)

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)
    list_filter = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('shops',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'model')
    search_fields = ('name', 'model', 'category__name')
    list_filter = ('category',)
    list_editable = ('model',)

class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'shop', 'description', 'price', 'quantity', 'price_rrc')
    search_fields = ('product__name', 'shop__name', 'description')
    list_filter = ('product', 'shop')
    list_editable = ('description', 'price', 'quantity', 'price_rrc')
    raw_id_fields = ('product', 'shop')

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')
    search_fields = ('value', 'parameter__name')
    list_filter = ('parameter',)
    raw_id_fields = ('product_info', 'parameter')

    def product_info(self, obj):
        return f"{obj.product_info.product.name} ({obj.product_info.shop.name})"
    product_info.short_description = 'Product Info'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'dt')
    search_fields = ('user__name', 'status')
    list_filter = ('status',)
    ordering = ('-dt',)
    raw_id_fields = ('user',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'shop', 'quantity')
    search_fields = ('order__id', 'product__name', 'shop__name')
    list_filter = ('order',)
    raw_id_fields = ('order', 'product', 'shop')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'value', 'city', 'street', 'house')
    search_fields = ('user__name', 'type', 'city', 'street')
    list_filter = ('type',)
    list_editable = ('city', 'street', 'house')
    raw_id_fields = ('user',)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_customer', 'is_supplier')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom fields', {'fields': ('is_customer', 'is_supplier')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_customer', 'is_supplier'),
        }),
    )

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
