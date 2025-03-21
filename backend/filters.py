# Django
from django_filters import rest_framework as filters
from django.db.models import QuerySet

# Local imports
from .models import Product, Shop, Category

# Standard library imports
from django.db.models import QuerySet
from typing import Optional

class ProductFilter(filters.FilterSet):
    """
    Фильтр для модели Product, позволяющий фильтровать продукты по магазину и категории.
    """
    shop = filters.NumberFilter(
        field_name="product_infos__shop", 
        method="filter_shop",
        required=False
    )
    category = filters.ModelChoiceFilter(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Product
        fields = ['category']

    def filter_shop(self, queryset: QuerySet[Product], name: str, value: Optional[Shop]) -> QuerySet[Product]:
        """
        Фильтрует продукты по выбранному магазину.
        
        Если значение магазина указано, возвращает только те продукты,
        которые связаны с указанным магазином. В противном случае возвращает
        исходный queryset.
        """
        if value:
            return queryset.filter(product_infos__shop=value)
        return queryset
