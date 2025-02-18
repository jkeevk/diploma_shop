from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import (
    Product,
    ProductInfo,
    ProductParameter,
    Parameter,
    Category,
    Shop,
    User,
    Contact,
    Order,
    OrderItem,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name"]

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ["name"]

class ProductInfoSerializer(serializers.ModelSerializer):
    parameters = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ["shop", "quantity", "price", "price_rrc", "parameters"]

    @extend_schema_field(serializers.DictField)
    def get_parameters(self, obj) -> dict:
        parameters = obj.product_parameters.all()
        return {param.parameter.name: param.value for param in parameters}

class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.SlugRelatedField(
        slug_field="name", queryset=Parameter.objects.all()
    )

    class Meta:
        model = ProductParameter
        fields = ["parameter", "value"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product_infos = ProductInfoSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "model", "category", "product_infos"]

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        product_infos_data = validated_data.pop('product_infos')

        category, created = Category.objects.get_or_create(**category_data)
        product = Product.objects.create(category=category, **validated_data)

        for product_info_data in product_infos_data:
            parameters_data = product_info_data.pop('parameters', [])
            shop_data = product_info_data.get('shop')

            product_info, created = ProductInfo.objects.get_or_create(
                product=product,
                shop=shop_data,
                defaults=product_info_data
            )

            for param_data in parameters_data:
                parameter_name = param_data.get('parameter')
                value = param_data.get('value')
                parameter, _ = Parameter.objects.get_or_create(name=parameter_name)
                ProductParameter.objects.update_or_create(
                    product_info=product_info,
                    parameter=parameter,
                    defaults={'value': value}
                )

        return product

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        product_infos_data = validated_data.pop('product_infos', None)

        if category_data:
            category, created = Category.objects.get_or_create(**category_data)
            instance.category = category

        instance.name = validated_data.get('name', instance.name)
        instance.model = validated_data.get('model', instance.model)
        instance.save()

        if product_infos_data is not None:
            for product_info_data in product_infos_data:
                parameters_data = product_info_data.pop('parameters', [])
                shop_data = product_info_data.get('shop')

                product_info_id = product_info_data.get('id', None)
                if product_info_id:
                    product_info = ProductInfo.objects.get(id=product_info_id, product=instance)
                    for attr, value in product_info_data.items():
                        setattr(product_info, attr, value)
                    product_info.save()
                else:
                    product_info, _ = ProductInfo.objects.get_or_create(
                        product=instance,
                        shop=shop_data,
                        defaults=product_info_data
                    )

                for param_data in parameters_data:
                    parameter_name = param_data.get('parameter')
                    value = param_data.get('value')
                    parameter, _ = Parameter.objects.get_or_create(name=parameter_name)
                    ProductParameter.objects.update_or_create(
                        product_info=product_info,
                        parameter=parameter,
                        defaults={'value': value}
                    )

        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "is_customer",
            "is_supplier",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        is_customer = data.get("is_customer", False)
        is_supplier = data.get("is_supplier", False)

        if is_customer and is_supplier:
            raise serializers.ValidationError(
                "Пользователь не может быть одновременно и продавцом, и покупателем."
            )
        if not is_customer and not is_supplier:
            raise serializers.ValidationError(
                "Пользователь должен быть либо продавцом, либо покупателем."
            )

        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                f"Ошибка валидации пароля: {', '.join(e.messages)}"
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_customer=validated_data["is_customer"],
            is_supplier=validated_data["is_supplier"],
            is_active=False,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_customer",
            "is_supplier",
        ]


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
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
    product_name = serializers.CharField(source="product.name", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "shop_name", "quantity", "total_price"]

    @extend_schema_field(serializers.FloatField)
    def get_total_price(self, obj) -> float:
        return obj.cost()


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "order_items", "dt", "status", "total_cost"]

        @extend_schema_field(serializers.FloatField)
        def get_total_cost(self, obj) -> float:
            return sum(
                item.quantity * item.product.price for item in obj.order_items.all()
            )


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        user.reset_password = {"token": token, "uid": uid}
        user.save()
