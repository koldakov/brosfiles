from django.urls import path

from api.v1.views import StripeWebhook

urlpatterns = [
    path('webhooks/stripe/', StripeWebhook.as_view(), name='stripe_webhook'),
]
