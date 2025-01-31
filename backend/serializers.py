from rest_framework import serializers
from .models import Product, ProductInfo, ProductParameter, Parameter, Category, Shop


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['name']


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.SlugRelatedField(slug_field='name', queryset=Parameter.objects.all())

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']

class ProductInfoSerializer(serializers.ModelSerializer):
    parameters = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ['id', 'shop', 'quantity', 'price', 'price_rrc', 'parameters']

    def get_parameters(self, obj):
        # Получаем все параметры для данного ProductInfo
        parameters = obj.product_parameters.all()
        return {param.parameter.name: param.value for param in parameters}

class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    price_rrc = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    quantity = serializers.IntegerField(write_only=True, required=False)
    description = serializers.CharField(write_only=True, required=False)
    parameters = serializers.JSONField(write_only=True, required=False)
    shop_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'model', 'price', 'price_rrc', 'quantity', 'description', 'parameters', 'shop_name']

    def create(self, validated_data):
        # Извлекаем данные для ProductInfo и ProductParameter
        price = validated_data.pop('price', None)
        price_rrc = validated_data.pop('price_rrc', None)
        quantity = validated_data.pop('quantity', None)
        description = validated_data.pop('description', '')  # Новое поле
        parameters_data = validated_data.pop('parameters', {})
        shop_name = validated_data.pop('shop_name', 'Default Shop')

        # Создаем объект Product
        product = Product.objects.create(**validated_data)

        # Получаем или создаем магазин
        shop, _ = Shop.objects.get_or_create(name=shop_name)

        # Создаем объект ProductInfo
        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            description=description,
            price=price if price is not None else 0,
            price_rrc=price_rrc if price_rrc is not None else 0,
            quantity=quantity if quantity is not None else 0
        )

        # Создаем параметры продукта
        for param_name, param_value in parameters_data.items():
            parameter, _ = Parameter.objects.get_or_create(name=param_name)
            ProductParameter.objects.create(
                product_info=product_info,
                parameter=parameter,
                value=param_value
            )

        return product

    def update(self, instance, validated_data):
        # Обновляем поля Product, если они переданы
        instance.name = validated_data.get('name', instance.name)
        instance.category_id = validated_data.get('category', instance.category_id)
        instance.model = validated_data.get('model', instance.model)
        instance.save()

        # Получаем или создаем магазин, если передан shop_name
        shop_name = validated_data.get('shop_name')
        if shop_name:
            shop, _ = Shop.objects.get_or_create(name=shop_name)
        else:
            shop = instance.product_infos.first().shop if instance.product_infos.first() else None

        # Получаем или создаем ProductInfo
        product_info = instance.product_infos.first()
        if not product_info and shop:
            product_info = ProductInfo.objects.create(
                product=instance,
                shop=shop,
                description='',
                price=0,
                price_rrc=0,
                quantity=0
            )

        # Обновляем поля ProductInfo, если они переданы
        if product_info:
            product_info.price = validated_data.get('price', product_info.price)
            product_info.price_rrc = validated_data.get('price_rrc', product_info.price_rrc)
            product_info.quantity = validated_data.get('quantity', product_info.quantity)
            product_info.description = validated_data.get('description', product_info.description)  # Новое поле
            if shop_name:
                product_info.shop = shop
            product_info.save()

        # Обновляем параметры продукта, если они переданы
        parameters_data = validated_data.get('parameters')
        if parameters_data and product_info:
            for param_name, param_value in parameters_data.items():
                parameter, _ = Parameter.objects.get_or_create(name=param_name)
                product_parameter, created = ProductParameter.objects.get_or_create(
                    product_info=product_info,
                    parameter=parameter,
                    defaults={'value': param_value}
                )
                if not created:
                    product_parameter.value = param_value
                    product_parameter.save()

        # Возвращаем обновленный объект
        return instance

    def to_representation(self, instance):
        # Переопределяем метод, чтобы вернуть данные в нужном формате
        representation = super().to_representation(instance)
        product_info = instance.product_infos.first()

        if product_info:
            representation['price'] = product_info.price
            representation['price_rrc'] = product_info.price_rrc
            representation['quantity'] = product_info.quantity
            representation['description'] = product_info.description  # Новое поле
            representation['shop_name'] = product_info.shop.name

            # Добавляем параметры продукта
            parameters = product_info.product_parameters.all()
            representation['parameters'] = {param.parameter.name: param.value for param in parameters}
        else:
            representation['price'] = 0.0
            representation['price_rrc'] = 0.0
            representation['quantity'] = 0
            representation['description'] = ''  # Новое поле
            representation['parameters'] = {}
            representation['shop_name'] = "Default Shop"

        return representation