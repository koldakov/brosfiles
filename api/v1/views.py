from http import HTTPStatus

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from payments.core import stripe
from payments.models import get_payment_instance, Subscription


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(View):
    def post(self, request, *args, **kwargs):
        try:
            signature = request.headers['Stripe-Signature']
        except KeyError:
            return HttpResponse(status=HTTPStatus.FORBIDDEN)

        try:
            event = stripe.Webhook.construct_event(request.body, signature, settings.STRIPE_ENDPOINT_SECRET)
        except ValueError as e:
            return HttpResponse(status=HTTPStatus.FORBIDDEN)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=HTTPStatus.FORBIDDEN)

        print(event.data.object.object)
        if event.type == 'checkout.session.completed':
            self.checkout_session_completed(event)
        elif event.type == 'invoice.payment_succeeded':
            self.invoice_payment_succeeded(event)
        elif event.type == 'customer.subscription.updated':
            self.customer_subscription_updated(event)

        return HttpResponse(status=HTTPStatus.OK)

    @staticmethod
    def customer_subscription_updated(event: stripe.Event):
        payment_instance = Subscription.objects.get(psp_id=event.data.object.id)
        payment_instance.update_from_event(event)

    @staticmethod
    def checkout_session_completed(event: stripe.Event):
        payment_instance = get_payment_instance(event)
        payment_instance.from_event(event, save=True)

    @staticmethod
    def invoice_payment_succeeded(event: stripe.Event):
        pass
