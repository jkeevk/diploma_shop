from django.contrib import admin
from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact

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
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'shop', 'price', 'quantity', 'price_rrc')
    search_fields = ('name', 'product__name', 'shop__name')
    list_filter = ('product', 'shop')

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')
    search_fields = ('value', 'parameter__name')
    list_filter = ('parameter',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'dt')
    search_fields = ('user__name', 'status')
    list_filter = ('status',)
    ordering = ('-dt',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'shop', 'quantity')
    search_fields = ('order__id', 'product__name', 'shop__name')
    list_filter = ('order',)

class ContactAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'value')
    search_fields = ('user__name', 'type')
    list_filter = ('type',)

admin.site.register(User, UserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Contact, ContactAdmin)
