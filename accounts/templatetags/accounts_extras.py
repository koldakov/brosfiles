from django import template

from accounts.models import ProductBase, User

register = template.Library()


@register.simple_tag
def get_product_internal_info(product: ProductBase, user: User):
    return product.get_internal_info(user)
