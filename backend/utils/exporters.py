from backend.models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
)
from typing import List, Dict


def generate_import_data() -> List[Dict[str, List[Dict]]]:
    """
    Генерирует данные для импорта из базы данных для различных сущностей: магазинов, категорий, товаров,
    информации о товарах, параметров и параметров товаров.
    """
    data = []

    shops = Shop.objects.all()
    shop_data = [{"name": shop.name, "url": shop.url} for shop in shops]
    data.append({"shops": shop_data})

    categories = Category.objects.all()
    category_data = [
        {"id": category.id, "name": category.name} for category in categories
    ]
    data.append({"categories": category_data})

    products = Product.objects.all()
    product_data = []
    for product in products:
        product_info = {
            "id": product.id,
            "name": product.name,
            "model": product.model,
            "category": product.category.name,
        }
        product_data.append(product_info)
    data.append({"products": product_data})

    product_infos = ProductInfo.objects.all()
    product_info_data = []
    for info in product_infos:
        product_info = {
            "product": info.product.name,
            "shop": info.shop.name,
            "external_id": info.external_id,
            "description": info.description,
            "quantity": info.quantity,
            "price": float(info.price),
            "price_rrc": float(info.price_rrc),
        }
        product_info_data.append(product_info)
    data.append({"product_infos": product_info_data})

    parameters = Parameter.objects.all()
    parameter_data = [{"id": param.id, "name": param.name} for param in parameters]
    data.append({"parameters": parameter_data})

    product_parameters = ProductParameter.objects.all()
    product_parameter_data = []
    for param in product_parameters:
        product_parameter = {
            "product_info": param.product_info.description,
            "parameter": param.parameter.name,
            "value": param.value,
        }
        product_parameter_data.append(product_parameter)
    data.append({"product_parameters": product_parameter_data})

    return data
