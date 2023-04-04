from django import template

from accounts.models import User
from payments.models import Price, Product

register = template.Library()


@register.simple_tag
def get_product_internal_info(product: Product, user: User):
    return {}


@register.simple_tag
def get_hprice(price: Price):
    return price.unit_amount / 100
