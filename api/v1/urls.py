from django.conf import settings
from django.urls import path

from api.v1.views import ObtainTokenView, UsersView, RefreshView, SignUpView, StripeWebhook

urlpatterns = [
    path('webhooks/stripe/', StripeWebhook.as_view(), name='stripe_webhook'),
]


if settings.ENABLE_API:
    urlpatterns += [
        path('auth/tokens/obtain/', ObtainTokenView.as_view(), name='auth-sign-in'),
        path('auth/sign-up/', SignUpView.as_view(), name='auth-sign-up'),
        path('auth/tokens/refresh/', RefreshView.as_view(), name='auth-tokens-refresh'),
        path('users/', UsersView.as_view(), name='users'),
    ]
