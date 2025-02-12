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
)


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
        fields = ["id", "shop", "quantity", "price", "price_rrc", "parameters"]

    def get_parameters(self, obj):
        parameters = obj.product_parameters.all()
        return {param.parameter.name: param.value for param in parameters}


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "category", "model"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_info = instance.product_infos.first()

        if product_info:
            representation["price"] = product_info.price
            representation["price_rrc"] = product_info.price_rrc
            representation["quantity"] = product_info.quantity
            representation["description"] = product_info.description
            representation["shop_name"] = product_info.shop.name

            parameters = product_info.product_parameters.all()
            representation["parameters"] = {
                param.parameter.name: param.value for param in parameters
            }
        else:
            representation["price"] = 0.0
            representation["price_rrc"] = 0.0
            representation["quantity"] = 0
            representation["description"] = ""
            representation["parameters"] = {}
            representation["shop_name"] = "Default Shop"

        return representation

    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        shop, _ = Shop.objects.get_or_create(name="Default Shop")
        ProductInfo.objects.create(
            product=product,
            shop=shop,
            description="",
            price=0,
            price_rrc=0,
            quantity=0,
        )

        return product

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.category_id = validated_data.get("category", instance.category_id)
        instance.model = validated_data.get("model", instance.model)
        instance.save()

        product_info = instance.product_infos.first()
        if not product_info:
            shop, _ = Shop.objects.get_or_create(name="Default Shop")
            product_info = ProductInfo.objects.create(
                product=instance,
                shop=shop,
                description="",
                price=0,
                price_rrc=0,
                quantity=0,
            )

        return instance


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "is_customer", "is_supplier")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class OrderSendMailSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    user_name = serializers.CharField()
    order_details = serializers.CharField()

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()