from http import HTTPStatus
import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import stripe


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(View):
    def post(self, request, *args, **kwargs):
        try:
            sig_header = request.headers['Stripe-Signature']
        except KeyError:
            return HttpResponse(status=HTTPStatus.FORBIDDEN)

        try:
            event = stripe.Webhook.construct_event(
                request.body, sig_header, settings.STRIPE_ENDPOINT_SECRET
            )
        except ValueError as e:
            raise PermissionDenied()
        except stripe.error.SignatureVerificationError as verification_err:
            return HttpResponse(status=HTTPStatus.FORBIDDEN)

        return HttpResponse(status=HTTPStatus.OK)
