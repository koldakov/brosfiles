from django import template

from accounts.models import Subscription, User

register = template.Library()


@register.simple_tag
def get_product_internal_info(subscription: Subscription, user: User):
    return subscription.get_internal_info(user)
