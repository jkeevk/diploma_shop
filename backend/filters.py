from django_filters import rest_framework as filters
from .models import Product, Shop, Category

class ProductFilter(filters.FilterSet):
    shop = filters.ModelChoiceFilter(queryset=Shop.objects.all(), method='filter_shop', required=False)
    category = filters.ModelChoiceFilter(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Product
        fields = ['category']

    def filter_shop(self, queryset, name, value):
        if value:
            return queryset.filter(product_infos__shop=value)
        return queryset