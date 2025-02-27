# Django
from django_filters import rest_framework as filters

# Local imports
from .models import Product, Shop, Category

class ProductFilter(filters.FilterSet):
    """
    Фильтр для модели Product, позволяющий фильтровать продукты по магазину и категории.
    """
    shop = filters.ModelChoiceFilter(queryset=Shop.objects.all(), method='filter_shop', required=False)
    category = filters.ModelChoiceFilter(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Product
        fields = ['category']

    def filter_shop(self, queryset, name, value):
        """
        Фильтрует продукты по выбранному магазину.
        
        Если значение магазина указано, возвращает только те продукты,
        которые связаны с указанным магазином. В противном случае возвращает
        исходный queryset.
        """
        if value:
            return queryset.filter(product_infos__shop=value)
        return queryset