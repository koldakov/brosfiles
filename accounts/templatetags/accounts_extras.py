from django import template

from accounts.models import Product, User

register = template.Library()


@register.simple_tag
def get_product_internal_info(product: Product, user: User):
    return product.get_internal_info(user)
