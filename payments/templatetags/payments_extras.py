from django import template

from accounts.models import User
from payments.models import ProductBase

register = template.Library()


@register.simple_tag
def get_product_internal_info(product: ProductBase, user: User):
    return product.get_internal_info(user)
