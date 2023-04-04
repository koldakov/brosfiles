import datetime

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from base.utils import generate_jwt_signature
from payments.core import stripe


class Product(models.Model):
    active = models.BooleanField(
        _('Active'),
        default=False
    )
    description = models.CharField(
        _('Description'),
        max_length=256,
        null=True,
        blank=True
    )
    psp_id = models.CharField(
        _('PSP ID'),
        max_length=64,
        editable=True,
        null=False,
        blank=False
    )
    metadata = models.JSONField(
        _('Metadata'),
        null=True,
        blank=True
    )
    name = models.CharField(
        _('Description'),
        max_length=256,
        null=True,
        blank=True
    )
    object_name = models.CharField(
        _('Object name'),
        max_length=16,
        editable=True,
        null=False,
        blank=False
    )
    product_type = models.CharField(
        _('Product type'),
        max_length=32,
        editable=True,
        null=False,
        blank=False
    )

    @staticmethod
    def populate(products: list = None):
        """Populates products from PSP.

        TODO: Optimise method, for now it's not critical.
        Method is not optimised and inserts all records 1 by 1.
        But this method won't be called often.

        Args:
            products (list, optional): list of products.
        """
        if products is None:
            # TODO: change limit=100 to starting_after=product_id
            products = stripe.Product.list(limit=100).data

        # TODO: Change to bulk update
        for product in products:
            product_obj, created = Product.objects.get_or_create(psp_id=product.id)

            product_obj.active = product.active
            product_obj.description = product.description
            product_obj.metadata = product.metadata.to_dict()
            product_obj.name = product.name
            product_obj.object_name = product.object
            product_obj.product_type = product.type
            product_obj.product_type = product.type

            product_obj.save()

    def is_available(self):
        return self.active


class Price(models.Model):
    active = models.BooleanField(
        _('Active'),
        default=False
    )
    billing_scheme = models.CharField(
        _('Billing scheme'),
        max_length=128,
        editable=True,
        null=False,
        blank=False
    )
    currency = models.CharField(
        _('Currency'),
        max_length=8,
        editable=True,
        null=False,
        blank=False
    )
    psp_id = models.CharField(
        _('PSP ID'),
        max_length=64,
        editable=True,
        null=False,
        blank=False
    )
    metadata = models.JSONField(
        _('Metadata'),
        null=True,
        blank=True
    )
    object_name = models.CharField(
        _('Object name'),
        max_length=16,
        editable=True,
        null=False,
        blank=False
    )
    recurring = models.JSONField(
        _('Recurring'),
        null=True,
        blank=True
    )
    payment_type = models.CharField(
        _('Payment type'),
        max_length=32,
        editable=True,
        null=False,
        blank=False
    )
    unit_amount = models.PositiveIntegerField(
        _('Unit amount'),
        null=False,
        blank=False
    )
    unit_amount_decimal = models.CharField(
        _('Unit amount decimal'),
        max_length=32,
        null=False,
        blank=False
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='prices',
        null=True,
        blank=True
    )

    @staticmethod
    def populate():
        """Populates prices from PSP.

        TODO: Optimise method, for now it's not critical.
        Method is not optimised and inserts all records 1 by 1.
        But this method won't be called often.
        """
        # TODO: change limit=100 to starting_after=price_id
        price_list = stripe.Price.list(expand=['data.product'], limit=100)
        # We need to populate ``payments.models.Product`` first as ``payments.models.Price`` has
        # foreign key on ``payments.models.Product``.
        Product.populate(products=[price.product for price in price_list.data])

        for price in price_list.data:
            try:
                price_obj = Price.objects.get(psp_id=price.id)
            except Price.DoesNotExist:
                price_obj = Price(psp_id=price.id)

            price_obj.active = price.active
            price_obj.billing_scheme = price.billing_scheme
            price_obj.currency = price.currency.upper()
            price_obj.psp_id = price.id
            price_obj.metadata = price.metadata.to_dict()
            price_obj.object_name = price.object
            price_obj.recurring = price.recurring or {}
            price_obj.payment_type = price.type
            price_obj.unit_amount = price.unit_amount
            price_obj.unit_amount_decimal = price.unit_amount_decimal
            price_obj.product = Product.objects.get(psp_id=price.product.id)

            price_obj.save()

    def get_mode(self):
        if self.recurring:
            return 'subscription'
        return 'payment'

    def get_payment_session(self, user):
        if settings.PAYMENT_HOST.startswith(('http://', 'https://')):
            payment_host = settings.PAYMENT_HOST
        else:
            scheme = 'https'
            if settings.DEBUG:
                scheme = 'http'
            payment_host = '%s://%s' % (scheme, settings.PAYMENT_HOST)

        metadata = dict(
            user_id=user.id,
            product_id=self.product.id,
            price_id=self.id
        )
        metadata.update(self.metadata)
        hash_ = generate_jwt_signature({'price_id': self.id}, expiration_time=86400)
        session_kwargs = dict(
            line_items=[
                {
                    'price': self.psp_id,
                    'quantity': 1,
                },
            ],
            mode=self.get_mode(),
            success_url='%s%s?hash=%s' % (payment_host, reverse('payments:payment_success'), hash_),
            cancel_url='%s%s' % (payment_host, reverse('payments:product_prices', kwargs={'pk': self.product.id})),
            metadata=metadata
        )
        if user.psp_id is not None:
            session_kwargs.update(dict(customer=user.psp_id))

        return stripe.checkout.Session.create(**session_kwargs)


class PaymentBase(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='payments',
        null=False,
        blank=False
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='payments',
        null=False,
        blank=False
    )
    psp_id = models.CharField(
        _('PSP ID'),
        max_length=64,
        editable=True,
        null=False,
        blank=False
    )
    active = models.BooleanField(
        _('Active'),
        default=False
    )

    class Meta:
        abstract = True

    def from_event(self, event: stripe.Event, save=False):
        """Creates an object from stripe event.

        Args:
            event (stripe.Event): Stripe event.
            save (bool, optional): Save object before return.
        """
        raise NotImplementedError()

    def update_from_event(self, event: stripe.Event):
        raise NotImplementedError()


class Payment(PaymentBase):
    @classmethod
    def from_event(cls, event: stripe.Event, save=False):
        pass

    def update_from_event(self, event: stripe.Event):
        pass


class Subscription(PaymentBase):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        null=False,
        blank=False
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        null=False,
        blank=False
    )
    current_period_end = models.DateTimeField(
        _('Current period end'),
        default=datetime.datetime.now
    )

    @classmethod
    def from_event(cls, event: stripe.Event, save=False):
        product: Product = Product.objects.get(id=event.data.object.metadata.product_id)
        user: User = User.objects.get(id=event.data.object.metadata.user_id)
        user.configure_from_event(event)

        subscription = cls(
            user=user,
            product=product,
            psp_id=event.data.object.subscription
        )
        if save:
            subscription.save()

        return subscription

    def update_from_event(self, event: stripe.Event):
        self.current_period_end = datetime.datetime.utcfromtimestamp(event.data.object.current_period_end)
        self.active = True

        self.save(update_fields=['active', 'current_period_end'])


MODE_TO_PAYMENT_INSTANCE = {
    'subscription': Subscription,
    'payment': Payment,
}


def get_payment_instance(event: stripe.Event):
    try:
        return MODE_TO_PAYMENT_INSTANCE[event.data.object.mode]
    except KeyError:
        raise NotImplementedError()
