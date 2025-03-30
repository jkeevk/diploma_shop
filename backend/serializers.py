# Standard library imports
from typing import Dict, Any, Optional

# Django
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.db import transaction

# DRF Spectacular
from drf_spectacular.utils import extend_schema_field

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

# Rest Framework
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ["id", "name"]


class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Contact."""

    class Meta:
        model = Contact
        fields = "__all__"

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

        # Получаем или создаем новый заказ
        order, created = Order.objects.get_or_create(
            user=user, status="new", defaults=validated_data
        )

        # Обрабатываем все элементы заказа
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
    """Сериализатор для модели Parameter."""

    class Meta:
        model = Parameter
        fields = ["name"]


class ProductInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ProductInfo с дополнительным полем parameters."""

    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())
    parameters = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ["shop", "quantity", "price", "price_rrc", "parameters"]

    @extend_schema_field(serializers.DictField)
    def get_parameters(self, obj: ProductInfo) -> Dict[str, Any]:
        """Метод для получения параметров продукта в виде словаря."""
        parameters = obj.product_parameters.all()
        return {param.parameter.name: param.value for param in parameters}


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductParameter.
    """

    parameter = serializers.SlugRelatedField(
        slug_field="name", queryset=Parameter.objects.all()
    )

    class Meta:
        model = ProductParameter
        fields = ["parameter", "value"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product с вложенными сериализаторами для категории и информации о продукте.
    """

    category = CategorySerializer()
    product_infos = ProductInfoSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "model", "category", "product_infos"]

    def create(self, validated_data: Dict[str, Any]) -> Product:
        """
        Создание нового продукта с учетом вложенных данных.
        """
        category_data = validated_data.pop("category")
        product_infos_data = validated_data.pop("product_infos")

        category, created = Category.objects.get_or_create(**category_data)
        product = Product.objects.create(category=category, **validated_data)

        for product_info_data in product_infos_data:
            parameters_data = product_info_data.pop("parameters", [])
            shop_data = product_info_data.get("shop")

            product_info, created = ProductInfo.objects.get_or_create(
                product=product, shop=shop_data, defaults=product_info_data
            )

            for param_data in parameters_data:
                parameter_name = param_data.get("parameter")
                value = param_data.get("value")
                parameter, _ = Parameter.objects.get_or_create(name=parameter_name)
                ProductParameter.objects.update_or_create(
                    product_info=product_info,
                    parameter=parameter,
                    defaults={"value": value},
                )

        return product

    def update(self, instance: Product, validated_data: Dict[str, Any]) -> Product:
        """
        Обновление продукта с учётом вложенных данных.
        """
        if "category" in validated_data:
            category_data = validated_data.pop("category")
            category, _ = Category.objects.get_or_create(**category_data)
            instance.category = category

        instance.name = validated_data.get("name", instance.name)
        instance.model = validated_data.get("model", instance.model)
        instance.save()

        if "product_infos" in validated_data:
            product_infos_data = validated_data.pop("product_infos")
            for product_info_data in product_infos_data:
                shop = product_info_data.get("shop")
                parameters_data = product_info_data.pop("parameters", [])
                if "id" in product_info_data:
                    product_info = ProductInfo.objects.get(
                        id=product_info_data["id"], product=instance
                    )
                    if product_info.shop.id != shop.id:
                        product_info.shop = shop
                    for key, value in product_info_data.items():
                        if key not in ["id", "shop"]:
                            setattr(product_info, key, value)
                    product_info.save()

                else:
                    product_info = ProductInfo.objects.create(
                        product=instance,
                        **{k: v for k, v in product_info_data.items() if k != "id"},
                    )

                for param_data in parameters_data:
                    parameter_name = param_data["parameter"]
                    value = param_data["value"]
                    parameter, _ = Parameter.objects.get_or_create(name=parameter_name)
                    ProductParameter.objects.update_or_create(
                        product_info=product_info,
                        parameter=parameter,
                        defaults={"value": value},
                    )

        return instance


class ShopSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Shop."""

    class Meta:
        model = Shop
        fields = ["id", "name", "url", "user"]

    def create(self, validated_data: Dict[str, Any]) -> Shop:
        """
        Создает магазин, если он не существует.
        Если магазин с таким именем или URL уже существует, возвращает его.
        """
        name = validated_data.get("name")
        url = validated_data.get("url")
        user = validated_data.get("user")

        shop, created = Shop.objects.get_or_create(
            name=name,
            defaults={"url": url, "user": user},
        )

        if not created:
            shop.url = url
            shop.user = user
            shop.save()

        return shop


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
