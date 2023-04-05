from payments.core import stripe
from payments.models import get_payment_instance, Subscription


class StripeWebhookService:
    def __init__(self, event: stripe.Event):
        self.event = event

    def procces_post_request(self):
        if self.event.type == 'checkout.session.completed':
            self.checkout_session_completed()
        elif self.event.type == 'invoice.payment_succeeded':
            self.invoice_payment_succeeded()
        elif self.event.type == 'customer.subscription.updated':
            self.customer_subscription_updated()

    def customer_subscription_updated(self):
        payment_instance = Subscription.objects.get(psp_id=self.event.data.object.id)
        payment_instance.update_from_event(self.event)

    def checkout_session_completed(self):
        payment_instance = get_payment_instance(self.event)
        payment_instance.from_event(self.event, save=True)

    def invoice_payment_succeeded(self):
        pass
