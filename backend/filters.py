# Django
from django_filters import rest_framework as filters
from django.db.models import QuerySet
from django.core.exceptions import PermissionDenied

# Local imports
from .models import Product, Shop, Category, Order, Contact, User

# Standard library imports
from django.db.models import QuerySet
from typing import Optional


class BasketFilter(filters.FilterSet):
    """Фильтр для модели Order, позволяющий фильтровать заказы по статусу."""

    status = filters.ChoiceFilter(choices=Order.STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ["status"]


class CategoryFilter(filters.FilterSet):
    """
    Фильтр для модели Category, позволяющий фильтровать категории по названию.
    """

    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        help_text="Фильтр по названию категории (частичное совпадение, без учета регистра)",
    )

    class Meta:
        model = Category
        fields = ["name"]


class ContactFilter(filters.FilterSet):
    """Фильтр для модели Contact, позволяющий фильтровать контакты по пользователю."""

    user = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        method="filter_user",
        label="Фильтр по пользователю",
        error_messages={
            "invalid_choice": "Пользователь с ID %(value)s не существует",
            "invalid": "Некорректный формат ID пользователя",
        },
    )

    class Meta:
        model = Contact
        fields = ["user"]

    def filter_user(self, queryset, name, value):
        user = self.request.user

        if user.role != "admin":
            raise PermissionDenied(
                "Фильтрация по пользователю доступна только администраторам"
            )

        return queryset.filter(user=value)


class ProductFilter(filters.FilterSet):
    """
    Фильтр для модели Product, позволяющий фильтровать продукты по магазину и категории.
    """

    shop = filters.CharFilter(
        method="filter_shop",
        required=False,
    )
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(), required=False
    )

    class Meta:
        model = Product
        fields = ["category"]

    def filter_shop(
        self, queryset: QuerySet[Product], name: str, value: Optional[Shop]
    ) -> QuerySet[Product]:
        """
        Фильтрует продукты по выбранному магазину.

        Если значение магазина указано, возвращает только те продукты,
        которые связаны с указанным магазином. В противном случае возвращает
        исходный queryset.
        """

        try:
            shop_id = int(value)
            return queryset.filter(product_infos__shop_id=shop_id)
        except ValueError:
            return queryset
