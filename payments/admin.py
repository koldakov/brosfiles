from django.contrib import admin

from payments.models import Price, Product, Subscription


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
