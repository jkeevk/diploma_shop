# Standard library imports
from typing import Dict, Any
from decimal import Decimal

# Django
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.db import transaction

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
    UserRole,
)
from .validators import PhoneValidator

# Rest Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category с проверкой уникальности имени при создании."""

    name = serializers.CharField(
        error_messages={
            "blank": "Имя категории не может быть пустым",
            "required": "Имя категории обязательно для заполнения",
            "invalid": "Имя категории должно быть строкой",
            "null": "Категория не может быть пустой",
        }
    )

    class Meta:
        model = Category
        fields = ["id", "name"]

    def validate_name(self, value):
        """
        Валидация имени категории:
        - При создании: проверка уникальности (без учета регистра)
        - При обновлении: разрешено сохранение текущего имени
        """
        value = value.strip()
        instance = self.instance

        if instance and instance.name.lower() == value.lower():
            return value

        if (
            Category.objects.filter(name__iexact=value)
            .exclude(pk=instance.pk if instance else None)
            .exists()
        ):
            raise serializers.ValidationError("Категория с таким именем уже существует")

        return value


class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Contact с полной валидацией и русификацией ошибок."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        error_messages={
            "required": "Пользователь обязателен для заполнения",
            "does_not_exist": "Пользователь с таким ID не существует",
            "incorrect_type": "Некорректный тип данных для пользователя",
            "null": "Поле пользователя не может быть пустым",
            "invalid_choice": "Указанный пользователь не существует",
        },
    )

    phone = serializers.CharField(
        validators=[PhoneValidator()],
        error_messages={
            "blank": "Телефон не может быть пустым",
            "required": "Телефон обязателен для заполнения",
            "null": "Телефон не может быть пустым",
            "invalid": "Введите корректный номер телефона в формате +79991234567",
        },
    )

    city = serializers.CharField(
        error_messages={
            "blank": "Город не может быть пустым",
            "required": "Город обязателен для заполнения",
            "null": "Город не может быть пустым",
            "invalid": "Некорректный формат города",
        }
    )

    street = serializers.CharField(
        error_messages={
            "blank": "Улица не может быть пустой",
            "required": "Улица обязательна для заполнения",
            "null": "Улица не может быть пустой",
            "invalid": "Некорректный формат улицы",
        }
    )

    house = serializers.CharField(
        error_messages={
            "blank": "Дом не может быть пустым",
            "required": "Дом обязателен для заполнения",
            "null": "Дом не может быть пустым",
            "invalid": "Некорректный номер дома",
        }
    )

    structure = serializers.CharField(
        required=False,
        allow_null=True,
        error_messages={
            "blank": "Корпус не может быть пустым",
            "invalid": "Некорректный формат корпуса",
            "null": "Корпус не может быть пустым",
        },
    )

    building = serializers.CharField(
        required=False,
        allow_null=True,
        error_messages={
            "blank": "Строение не может быть пустым",
            "invalid": "Некорректный формат строения",
            "null": "Строение не может быть пустым",
        },
    )

    apartment = serializers.CharField(
        required=False,
        allow_null=True,
        error_messages={
            "blank": "Квартира не может быть пустой",
            "invalid": "Некорректный формат квартиры",
            "null": "Квартира не может быть пустой",
        },
    )

    class Meta:
        model = Contact
        fields = "__all__"
        extra_kwargs = {
            "user": {"error_messages": {"invalid": "Недопустимый ID пользователя"}}
        }

    def __init__(self, *args, **kwargs):
        """Инициализация сериализатора."""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.role != "admin":
            self.fields["user"].read_only = True

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация данных."""
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not self.partial:
            if user and user.role != "admin":
                data["user"] = user
                try:
                    contact = Contact(**data)
                    contact.clean()
                except ValidationError as e:
                    raise serializers.ValidationError(e.message)
                user_id_in_request = self.initial_data.get("user")
                if user_id_in_request is not None and str(user.id) != str(
                    user_id_in_request
                ):
                    raise serializers.ValidationError(
                        {"user": "Вы не можете указывать другого пользователя."}
                    )

        return data

    def create(self, validated_data: Dict[str, Any]) -> Contact:
        """Создание контакта."""
        user = self.context["request"].user
        if user.role != "admin":
            validated_data["user"] = user
        return super().create(validated_data)


class FileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов."""

    file = serializers.FileField()


class LoginSerializer(serializers.Serializer):
    """Сериализатор для аутентификации пользователя."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка учетных данных пользователя."""
        email = data.get("email")
        password = data.get("password")
        user = None

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                raise serializers.ValidationError(
                    "Не удалось войти с предоставленными учетными данными."
                )

        data["user"] = user
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderItem."""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), error_messages={"null": "Не указан товар"}
    )
    shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), error_messages={"null": "Не указан магазин"}
    )
    quantity = serializers.IntegerField(
        error_messages={
            "required": "Обязательное поле не указано",
            "invalid": "Некорректное количество",
        }
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "shop", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order с вложенными элементами заказа."""

    order_items = OrderItemSerializer(many=True, required=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        error_messages={
            "required": "Пользователь не указан",
            "does_not_exist": "Указанный пользователь не существует",
        },
    )
    status = serializers.ChoiceField(
        choices=Order.STATUS_CHOICES,
        required=False,
        default="new",
        error_messages={
            "invalid_choice": "Недопустимый статус заказа. Доступные варианты: {choices}".format(
                choices=", ".join([choice[0] for choice in Order.STATUS_CHOICES])
            )
        },
    )

    class Meta:
        model = Order
        fields = ["id", "user", "order_items", "dt", "status"]
        extra_kwargs = {
            "dt": {"read_only": True},
            "order_items": {
                "error_messages": {"required": "Список товаров обязателен"}
            },
        }

    def _validate_shop(self, shop: Shop) -> None:
        """Валидация данных магазина."""
        if not shop.user:
            raise serializers.ValidationError(
                f"Магазин {shop.name} (ID={shop.id}) не привязан к пользователю"
            )

        if not shop.user.is_active:
            raise serializers.ValidationError(
                f"Продавец {shop.user.email} (магазин ID={shop.id}) неактивен"
            )

    def _validate_product_availability(
        self, product: Product, shop: Shop, quantity: int
    ) -> ProductInfo:
        """Проверка доступности товара."""
        product_info = ProductInfo.objects.filter(product=product, shop=shop).first()

        if not product_info:
            raise serializers.ValidationError(
                f"Товар {product.name} (ID={product.id}) отсутствует в магазине {shop.name}"
            )

        if product_info.quantity < quantity:
            raise serializers.ValidationError(
                f"Недостаточно товара {product.name}. Доступно: {product_info.quantity}"
            )

        return product_info

    def _process_order_item(self, order: Order, item_data: dict) -> None:
        """Обработка одного элемента заказа."""
        product = item_data["product"]
        shop = item_data["shop"]
        quantity = item_data["quantity"]

        self._validate_shop(shop)
        product_info = self._validate_product_availability(product, shop, quantity)

        existing_item = OrderItem.objects.filter(
            order=order, product=product, shop=shop
        ).first()

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if product_info.quantity < new_quantity:
                raise serializers.ValidationError(
                    f"Превышение доступного количества товара {product.name}. Максимум: {product_info.quantity}"
                )
            existing_item.quantity = new_quantity
            existing_item.save()
        else:
            OrderItem.objects.create(
                order=order, product=product, shop=shop, quantity=quantity
            )

    @transaction.atomic
    def create(self, validated_data: dict) -> Order:
        """Создание заказа с обработкой элементов."""
        order_items_data = validated_data.pop("order_items")
        user = validated_data.pop("user", self.context["request"].user)

        order, created = Order.objects.get_or_create(
            user=user, status="new", defaults=validated_data
        )

        for item_data in order_items_data:
            self._process_order_item(order, item_data)

        return order

    def update(self, instance: Order, validated_data: Dict[str, Any]) -> Order:
        """Обновление существующего заказа с элементами заказа."""
        request = self.context.get("request")
        method = request.method if request else None

        if "status" in validated_data:
            instance.status = validated_data["status"]
        instance.save()

        order_items_data = validated_data.get("order_items")

        if method == "PUT":
            instance.order_items.all().delete()
            for item_data in order_items_data:
                self._validate_and_create_item(instance, item_data)

        elif method == "PATCH":
            for item_data in order_items_data:
                self._update_item_partially(instance, item_data)

        return instance

    def _update_item_partially(self, order: Order, item_data: dict):
        """Частичное обновление элемента заказа с валидацией"""
        item_filter = {}
        if "product" in item_data:
            item_filter["product"] = item_data["product"]
        if "shop" in item_data:
            item_filter["shop"] = item_data["shop"]

        existing_item = (
            order.order_items.filter(**item_filter).first() if item_filter else None
        )

        if not existing_item and not item_filter:
            existing_item = order.order_items.first()

        if not existing_item:
            raise serializers.ValidationError("Элемент заказа не найден для обновления")

        new_product = item_data.get("product", existing_item.product)
        new_shop = item_data.get("shop", existing_item.shop)
        new_quantity = item_data.get("quantity", existing_item.quantity)

        if "product" in item_data or "shop" in item_data:
            product_info = ProductInfo.objects.filter(
                product=new_product, shop=new_shop
            ).first()

        product_info = ProductInfo.objects.filter(
            product=new_product, shop=new_shop
        ).first()

        if product_info.quantity < new_quantity:
            raise serializers.ValidationError(
                f"Недостаточно товара {new_product.name} в магазине {new_shop.name}. "
                f"Доступно: {product_info.quantity}, запрошено: {new_quantity}."
            )

        for field in ["product", "shop", "quantity"]:
            if field in item_data:
                setattr(existing_item, field, item_data[field])

        existing_item.save()

    def _validate_and_create_item(self, order: Order, item_data: dict):
        """Валидация и создание элемента заказа."""
        try:
            shop = item_data["shop"]
            product = item_data["product"]
            quantity = item_data["quantity"]
        except KeyError as e:
            raise serializers.ValidationError(
                {str(e): "Обязательное поле не указано"}
            ) from e

        OrderItem.objects.create(
            order=order, product=product, shop=shop, quantity=quantity
        )


class OrderWithContactSerializer(serializers.ModelSerializer):
    """Сериализатор для подтверждения корзины с указанием контактной информации."""

    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        required=True,
        error_messages={
            "required": "ID контакта обязателен.",
            "does_not_exist": "Неверный ID контакта.",
            "incorrect_type": "Некорректный тип ID контакта.",
        },
    )

    class Meta:
        model = Order
        fields = ["contact_id"]

    def validate_contact_id(self, value):
        """Проверяет, принадлежит ли контакт текущему пользователю."""
        user = self.context["request"].user
        if not Contact.objects.filter(id=value.id, user=user).exists():
            raise serializers.ValidationError("Контакт не найден.")
        return value

    def validate(self, attrs):
        """Проверяет наличие корзины (заказа со статусом 'new')."""
        user = self.context["request"].user
        order = Order.objects.filter(user=user, status="new").first()

        if not order:
            raise serializers.ValidationError("Корзина пуста.")

        attrs["order"] = order
        return attrs

    def create(self, validated_data):
        """Обновляет существующий заказ, подтверждая его."""
        order = validated_data["order"]
        order.contact = validated_data["contact_id"]
        order.status = "confirmed"
        order.save()
        return order


class ParameterSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Parameter с проверкой уникальности имени."""

    name = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Parameter.objects.all(),
                message="Параметр с таким именем уже существует",
            )
        ],
        error_messages={
            "blank": "Имя параметра не может быть пустым",
            "required": "Имя параметра обязательно для заполнения",
            "invalid": "Имя параметра должно быть строкой",
            "null": "Параметр не может быть пустым",
        },
    )

    class Meta:
        model = Parameter
        fields = ["id", "name"]

    def validate_name(self, value):
        """
        Дополнительная валидация имени параметра:
        - проверка уникальности (без учета регистра)
        - удаление пробелов в начале/конце
        """

        value = value.strip()

        if Parameter.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Параметр с таким именем уже существует")
        return value


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductParameter.
    """

    parameter = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Parameter.objects.all(),
        error_messages={
            "required": "ID параметра обязателен.",
            "does_not_exist": "Неверный ID параметра.",
            "incorrect_type": "Некорректный тип ID параметра.",
            "invalid": "Некорректный ID параметра.",
            "null": "Параметр не может быть пустым",
        },
    )

    value = serializers.CharField(
        error_messages={
            "blank": "Значение параметра не может быть пустым",
            "required": "Значение параметра обязательно для заполнения",
            "null": "Значение параметра не может быть пустым",
            "invalid": "Некорректное значение параметра",
        }
    )

    class Meta:
        model = ProductParameter
        fields = ["parameter", "value"]


class ProductInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ProductInfo с полями параметров."""

    shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        error_messages={
            "required": "ID магазина обязателен.",
            "does_not_exist": "Неверный ID магазина.",
            "incorrect_type": "Некорректный тип ID магазина.",
        },
    )

    parameters = serializers.DictField(
        child=serializers.CharField(
            error_messages={
                "invalid": "Значение параметра должно быть строкой",
                "blank": "Значение параметра не может быть пустым",
                "required": "Значение параметра обязательно для заполнения",
            }
        ),
        write_only=True,
        error_messages={
            "required": "Параметры обязательны для заполнения.",
            "null": "Параметры не могут быть пустыми.",
            "invalid": "Некорректный формат параметров (ожидается словарь)",
        },
        required=False,
    )

    product_parameters = ProductParameterSerializer(
        many=True,
        read_only=True,
        error_messages={
            "required": "Параметры обязательны для заполнения.",
            "null": "Параметры не могут быть пустыми.",
            "invalid": "Некорректные параметры.",
        },
    )

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        error_messages={
            "required": "Цена обязательна для заполнения.",
            "invalid": "Некорректное число.",
            "min_value": "Цена должна быть больше 0.",
        },
    )

    price_rrc = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        error_messages={
            "invalid": "Некорректное число.",
            "min_value": "Цена должна быть больше 0.",
        },
    )

    external_id = serializers.CharField(
        error_messages={
            "blank": "Внешний ID не может быть пустым",
            "invalid": "Некорректный внешний ID",
        },
        required=False,
    )

    description = serializers.CharField(
        error_messages={
            "blank": "Описание не может быть пустым",
            "invalid": "Некорректное описание",
        },
        required=False,
    )

    def validate_price(self, value):
        if value < Decimal("0.01"):
            raise serializers.ValidationError("Цена должна быть больше 0.")
        return value

    def validate_price_rrc(self, value):
        if value < Decimal("0.01"):
            raise serializers.ValidationError("Цена должна быть больше 0.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Количество не может быть отрицательным.")
        return value

    quantity = serializers.IntegerField(
        error_messages={
            "invalid": "Требуется целое число.",
        },
        required=False,
    )

    class Meta:
        model = ProductInfo
        fields = [
            "shop",
            "external_id",
            "description",
            "quantity",
            "price",
            "price_rrc",
            "parameters",
            "product_parameters",
        ]


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product с вложенным сериализатором для информации о продукте.
    Категория обрабатывается через имя, а не объект.
    """

    name = serializers.CharField(
        error_messages={
            "required": "Название товара обязательно для заполнения.",
            "blank": "Название товара не может быть пустым.",
            "invalid": "Некорректное название товара.",
        }
    )

    model = serializers.CharField(
        error_messages={
            "blank": "Модель товара не может быть пустой.",
            "invalid": "Некорректная модель товара.",
        },
        required=False,
    )

    category = serializers.CharField(
        error_messages={
            "required": "Категория обязательна для заполнения.",
            "blank": "Категория не может быть пустой.",
            "invalid": "Некорректное имя категории.",
        }
    )

    product_infos = ProductInfoSerializer(
        many=True,
        error_messages={
            "required": "Информация о продукте обязательна для заполнения.",
            "blank": "Информация о продукте не может быть пустой.",
            "invalid": "Некорректная информация о продукте.",
            "null": "Информация о продукте не может быть пустой.",
        },
    )

    class Meta:
        model = Product
        fields = ["id", "name", "model", "category", "product_infos"]

    def create(self, validated_data: Dict[str, Any]) -> Product:
        """
        Создание нового продукта с учётом вложенных данных.
        """
        product_infos_data = validated_data.pop("product_infos")
        category_name = validated_data.pop("category")
        category, created = Category.objects.get_or_create(name=category_name)

        product = Product.objects.create(category=category, **validated_data)

        for product_info_data in product_infos_data:
            parameters_data = product_info_data.pop("parameters", {})
            product_info = ProductInfo.objects.create(
                product=product, shop=product_info_data.pop("shop"), **product_info_data
            )

            for param_name, param_value in parameters_data.items():
                parameter, _ = Parameter.objects.get_or_create(name=param_name)
                ProductParameter.objects.create(
                    product_info=product_info,
                    parameter=parameter,
                    value=param_value,
                )

        return product

    def update(self, instance: Product, validated_data: Dict[str, Any]) -> Product:
        is_partial = self.context["request"].method == "PATCH"

        if "category" in validated_data:
            category_name = validated_data.pop("category")
            category, _ = Category.objects.get_or_create(name=category_name)
            instance.category = category

        instance.name = validated_data.get("name", instance.name)
        instance.model = validated_data.get("model", instance.model)
        instance.save()

        product_infos_data = validated_data.pop("product_infos", None)

        if product_infos_data is not None:
            for product_info_data in product_infos_data:
                shop_id = product_info_data.pop("shop", None)

                if not shop_id:
                    if is_partial and instance.product_infos.exists():
                        product_info = instance.product_infos.first()
                    else:
                        raise serializers.ValidationError({"shop": "Обязательное поле"})
                else:
                    product_info = ProductInfo.objects.filter(
                        product=instance, shop_id=shop_id
                    ).first()

                if not product_info:
                    raise serializers.ValidationError(
                        {"shop": "Товар не связан с магазином"}
                    )

                for field in ["quantity", "price", "price_rrc"]:
                    if field in product_info_data:
                        setattr(product_info, field, product_info_data[field])
                product_info.save()

                if "parameters" in product_info_data:
                    parameters_data = product_info_data.pop("parameters")
                    product_info.product_parameters.all().delete()
                    for param_name, param_value in parameters_data.items():
                        parameter, _ = Parameter.objects.get_or_create(name=param_name)
                        ProductParameter.objects.create(
                            product_info=product_info,
                            parameter=parameter,
                            value=param_value,
                        )

        return instance


class ShopSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Shop."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        error_messages={
            "does_not_exist": "Пользователь с таким ID не существует",
            "incorrect_type": "Некорректный тип данных для пользователя",
        },
    )

    class Meta:
        model = Shop
        fields = ["id", "name", "url", "user"]
        extra_kwargs = {
            "name": {
                "error_messages": {
                    "blank": "Название магазина не может быть пустым",
                    "required": "Обязательное поле",
                    "invalid": "Некорректное название магазина",
                }
            },
            "url": {
                "required": False,
                "allow_blank": True,
                "error_messages": {"invalid": "Введите корректный URL-адрес"},
            },
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация данных с учетом ролей"""
        request = self.context.get("request")

        if attrs.get("user") and request.user.role != "admin":
            raise serializers.ValidationError(
                {"user": "Указание пользователя доступно только администраторам"}
            )

        if request.user.role != "admin" and "user" not in attrs:
            attrs["user"] = request.user

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Shop:
        """Создание магазина с обработкой URL"""
        request_user = self.context["request"].user
        name = validated_data["name"]
        url = validated_data.get("url")

        # Для администраторов
        if request_user.role == "admin":
            user = validated_data.get("user", request_user)

            if Shop.objects.filter(name=name, user=user).exists():
                raise serializers.ValidationError(
                    {"name": "Магазин с таким названием уже существует"}
                )
            return Shop.objects.create(name=name, url=url, user=user)

        # Для продавцов
        if Shop.objects.filter(name=name, user=request_user).exists():
            raise serializers.ValidationError(
                {"name": "Магазин с таким названием уже существует"}
            )
        if Shop.objects.filter(name=name).exclude(user=request_user).exists():
            raise serializers.ValidationError(
                {"name": "Магазин с таким названием уже существует у другого продавца"}
            )

        return Shop.objects.create(name=name, url=url, user=request_user)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """

    role = serializers.ChoiceField(
        choices=[(role.value, role.name) for role in UserRole],
        error_messages={
            "invalid_choice": "Неверная роль. Допустимые значения: {allowed_roles}".format(
                allowed_roles=", ".join([role.value for role in UserRole])
            ),
            "required": "Роль обязательна для заполнения",
            "blank": "Роль обязательна для заполнения",
        },
    )

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "role"]
        extra_kwargs = {
            "email": {
                "validators": [],
                "error_messages": {
                    "required": "Email обязателен для заполнения",
                    "blank": "Email обязателен для заполнения",
                    "invalid": "Введите корректный email адрес",
                },
            },
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "Пароль обязателен для заполнения",
                    "blank": "Пароль не может быть пустым",
                },
            },
        }

    def validate_email(self, value):
        """Проверка уникальности email."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_password(self, value):
        """Валидация сложности пароля."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        """Создание пользователя с неактивным аккаунтом."""
        return User.objects.create_user(is_active=False, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
        ]


class PasswordResetSerializer(serializers.Serializer):
    """Сериализатор для сброса пароля."""

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        """Проверка существования пользователя с указанным email."""
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError(
                {"email": ["Пользователь с таким email не найден."]},
                code="user_not_found",
            )
        return value

    def save(self) -> None:
        """Генерация токена для сброса пароля и сохранение его в модели пользователя."""
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        user.reset_password = {"token": token, "uid": uid}
        user.save()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения сброса пароля"""

    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Проверка валидности данных."""
        uidb64 = self.context.get("uidb64")
        token = self.context.get("token")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"uid": ["Недопустимый идентификатор пользователя"]}
            )

        if not default_token_generator.check_token(self.user, token):
            raise serializers.ValidationError(
                {"token": ["Недействительный токен сброса пароля"]}
            )

        try:
            validate_password(attrs["new_password"], self.user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})

        return attrs

    def save(self):
        """Сохранение нового пароля пользователя."""
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
