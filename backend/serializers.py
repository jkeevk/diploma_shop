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


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ["name"]


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.SlugRelatedField(
        slug_field="name", queryset=Parameter.objects.all()
    )

    class Meta:
        model = ProductParameter
        fields = ["parameter", "value"]


class ProductInfoSerializer(serializers.ModelSerializer):
    parameters = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ["shop", "quantity", "price", "price_rrc", "parameters"]

    @extend_schema_field(serializers.DictField)
    def get_parameters(self, obj) -> dict:
        parameters = obj.product_parameters.all()
        return {param.parameter.name: param.value for param in parameters}


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    product_infos = ProductInfoSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "model", "category", "product_infos"]


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = User
        fields = ["email", "password", "name", "surname", "is_customer", "is_supplier"]
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
                f"Пароль не прошел валидацию: {', '.join(e.messages)}"
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            surname=validated_data.get("surname", ""),
            is_customer=validated_data["is_customer"],
            is_supplier=validated_data["is_supplier"],
            is_active=False,
        )
        return user
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'surname', 'is_customer', 'is_supplier']

class OrderSendMailSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    user_name = serializers.CharField()
    order_details = serializers.CharField()


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
                    "Unable to log in with provided credentials."
                )
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        data["user"] = user
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'shop_name', 'quantity', 'total_price']

    @extend_schema_field(serializers.FloatField)
    def get_total_price(self, obj) -> float:
        return obj.cost()


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        total_cost = serializers.SerializerMethodField()
        fields = ['id', 'user', 'order_items', 'dt', 'status', 'total_cost']

        @extend_schema_field(serializers.FloatField)
        def get_total_cost(self, obj) -> float:
            return sum(item.quantity * item.product.price for item in obj.order_items.all())