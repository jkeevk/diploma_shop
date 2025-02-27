# Standard library imports
from typing import Dict, Any

# Django
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

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

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет данные перед созданием или обновлением контакта.
        """
        if not self.partial:
            try:
                contact = Contact(**data)
                contact.clean()
            except ValidationError as e:
                raise serializers.ValidationError(e.message)
        return data


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

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                raise serializers.ValidationError(
                    "Не удалось войти с предоставленными учетными данными."
                )
        else:
            raise serializers.ValidationError(
                "Необходимо указать 'email' и 'password'."
            )

        data["user"] = user
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderItem."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())

    class Meta:
        model = OrderItem
        fields = ["product", "shop", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order с вложенными элементами заказа."""

    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "order_items", "dt", "status"]

    def create(self, validated_data: Dict[str, Any]) -> Order:
        """Создание нового заказа с элементами заказа."""
        order_items_data = validated_data.pop("order_items")
        user = validated_data.pop("user", self.context["request"].user)

        for item_data in order_items_data:
            shop = item_data.get("shop")
            if shop and not shop.user.is_active:
                raise serializers.ValidationError(
                    f"Продавец {shop.user.email} (магазин ID={shop.id}) неактивен. Невозможно создать заказ."
                )

        for item_data in order_items_data:
            product = item_data.get("product")
            shop = item_data.get("shop")
            quantity = item_data.get("quantity")

            product_info = ProductInfo.objects.filter(
                product=product, shop=shop
            ).first()
            if not product_info:
                raise serializers.ValidationError(
                    f"Товар {product.name} (ID={product.id}) отсутствует в магазине {shop.name} (ID={shop.id})."
                )

            if product_info.quantity < quantity:
                raise serializers.ValidationError(
                    f"Недостаточно товара {product.name} (ID={product.id}) в магазине {shop.name} (ID={shop.id}). Доступно: {product_info.quantity}, запрошено: {quantity}."
                )

        order = Order.objects.filter(user=user, status="new").first()
        if not order:
            order = Order.objects.create(user=user, status="new")

        for item_data in order_items_data:
            product = item_data.get("product")
            shop = item_data.get("shop")
            quantity = item_data.get("quantity")

            existing_item = OrderItem.objects.filter(
                order=order, product=product, shop=shop
            ).first()

            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
            else:
                OrderItem.objects.create(
                    order=order, product=product, shop=shop, quantity=quantity
                )

            product_info = ProductInfo.objects.get(product=product, shop=shop)
            product_info.quantity -= quantity
            product_info.save()

        return order


class OrderWithContactSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order с указанием контактной информации."""

    contact_id = serializers.PrimaryKeyRelatedField(
        source="contact", queryset=Contact.objects.all(), required=False
    )

    class Meta:
        model = Order
        fields = ["contact_id"]

    def create(self, validated_data: Dict[str, Any]) -> Order:
        """Создание нового заказа с указанием контактной информации."""
        order_items_data = validated_data.pop("order_items", [])
        user = validated_data.pop("user", self.context["request"].user)

        order, created = Order.objects.get_or_create(user=user, status="new")

        for item_data in order_items_data:
            product = item_data.get("product")
            shop = item_data.get("shop")
            quantity = item_data.get("quantity")

            existing_item = OrderItem.objects.filter(
                order=order, product=product, shop=shop
            ).first()

            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
            else:
                OrderItem.objects.create(
                    order=order, product=product, shop=shop, quantity=quantity
                )

        return order


class ParameterSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Parameter."""

    class Meta:
        model = Parameter
        fields = ["name"]


class ProductInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ProductInfo с дополнительным полем parameters."""

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
    """Сериализатор для модели ProductParameter."""

    parameter = serializers.SlugRelatedField(
        slug_field="name", queryset=Parameter.objects.all()
    )

    class Meta:
        model = ProductParameter
        fields = ["parameter", "value"]


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product с вложенными сериализаторами для категории и информации о продукте."""

    category = CategorySerializer()
    product_infos = ProductInfoSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "model", "category", "product_infos"]

    def create(self, validated_data: Dict[str, Any]) -> Product:
        """Создание нового продукта с учетом вложенных данных."""
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
        """Обновление существующего продукта с учетом вложенных данных."""
        category_data = validated_data.pop("category", None)
        product_infos_data = validated_data.pop("product_infos", None)

        if category_data:
            category, created = Category.objects.get_or_create(**category_data)
            instance.category = category

        instance.name = validated_data.get("name", instance.name)
        instance.model = validated_data.get("model", instance.model)
        instance.save()

        if product_infos_data is not None:
            for product_info_data in product_infos_data:
                parameters_data = product_info_data.pop("parameters", [])
                shop_data = product_info_data.get("shop")

                product_info_id = product_info_data.get("id", None)
                if product_info_id:
                    product_info = ProductInfo.objects.get(
                        id=product_info_id, product=instance
                    )
                    for attr, value in product_info_data.items():
                        setattr(product_info, attr, value)
                    product_info.save()
                else:
                    product_info, _ = ProductInfo.objects.get_or_create(
                        product=instance, shop=shop_data, defaults=product_info_data
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
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "role": {"required": True},
        }

    def validate_role(self, value: str) -> str:
        """Проверка на корректность значения роли."""
        if value not in [role.value for role in UserRole]:
            raise serializers.ValidationError("Неверная роль пользователя.")
        return value

    def validate_email(self, value: str) -> str:
        """Проверка уникальности email."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_password(self, value: str) -> str:
        """Проверка валидности пароля."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                f"Ошибка валидации пароля: {', '.join(e.messages)}"
            )
        return value

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Создание нового пользователя."""
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=validated_data["role"],
            is_active=False,
        )
        return user


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
            raise serializers.ValidationError("Пользователь с таким email не найден.")
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
    """Сериализатор для подтверждения сброса пароля."""

    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value: str) -> str:
        """Проверка валидности нового пароля."""
        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
