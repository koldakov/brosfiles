from django import template

from accounts.models import File, User

register = template.Library()


@register.simple_tag
def get_product_internal_info(product, user: User):
    return product.get_internal_info(user)


@register.simple_tag
def user_has_file_delete_permission(file: File, user: User):
    return file.has_delete_permission(user)
