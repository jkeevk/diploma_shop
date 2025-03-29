from .schemas.user import USER_SCHEMAS
from .schemas.basket import BASKET_SCHEMAS
from .schemas.category import CATEGORY_SCHEMAS
from .schemas.contacts import CONTACT_SCHEMAS
from .schemas.parameters import PARAMETER_SCHEMAS
from .schemas.partners import PARTNER_SCHEMAS
from .schemas.products import PRODUCT_SCHEMAS
from .schemas.shops import SHOP_SCHEMAS
from .schemas.tests import TEST_SCHEMAS
from .schemas.users import USERS_SCHEMAS

SWAGGER_CONFIGS = {
    **USER_SCHEMAS,
    **BASKET_SCHEMAS,
    **CATEGORY_SCHEMAS,
    **CONTACT_SCHEMAS,
    **PARAMETER_SCHEMAS,
    **PARTNER_SCHEMAS,
    **PRODUCT_SCHEMAS,
    **SHOP_SCHEMAS,
    **TEST_SCHEMAS,
    **USERS_SCHEMAS,
}
