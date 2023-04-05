from django.conf import settings
from rest_framework.authentication import BaseAuthentication

from api.exceptions import AuthenticationFailedException
from payments.core import stripe


class StripeAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            signature = request.headers['Stripe-Signature']
        except KeyError:
            raise AuthenticationFailedException('SSO header is missing')
        try:
            event: stripe.Event = stripe.Webhook.construct_event(request.body, signature,
                                                                 settings.STRIPE_ENDPOINT_SECRET)
        except ValueError as e:
            raise AuthenticationFailedException()
        except stripe.error.SignatureVerificationError:
            raise AuthenticationFailedException()

        return None, event
