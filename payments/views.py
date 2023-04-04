from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from base.exceptions import FatalSignatureError, SignatureExpiredError
from base.utils import decode_jwt_signature
from payments.models import Price, Product


class ProductsView(View):
    template_name = 'payments/products.html'

    def get(self, request, *args, **kwargs):
        # TODO: Don't do like this
        products = Product.objects.all()

        return render(
            request,
            template_name=self.template_name,
            context={
                'products': products,
            }
        )

    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            messages.success(request, _('Please sign up first!'))
            return redirect(reverse('accounts:signup'))

        product_id = request.POST.get('product_id')

        if product_id is None:
            raise PermissionDenied()

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise PermissionDenied()

        return redirect('payments:product_prices', pk=product.id)


class ProcessPaymentView(LoginRequiredMixin, View):
    template_name = 'payments/payment.html'

    def get(self, request, *args, **kwargs):
        raise PermissionDenied()

    def post(self, request, *args, **kwargs):
        raise PermissionDenied()


class PaymentCallbackView(LoginRequiredMixin, View):
    template_name = 'payments/callbacks/payment.html'

    def get(self, request, *args, **kwargs):
        raise PermissionDenied()


class ProductView(View):
    template_name = 'payments/product_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            product_id = kwargs['pk']
        except KeyError:
            raise PermissionDenied()
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise PermissionDenied()

        return render(
            request,
            template_name=self.template_name,
            context={
                'product': product,
            }
        )

    def post(self, request, *args, **kwargs):
        price_id = request.POST.get('price_id')
        if price_id is None:
            raise PermissionDenied()

        try:
            price = Price.objects.get(id=price_id)
        except Price.DoesNotExist:
            raise PermissionDenied()

        payment_session = price.get_payment_session(request.user)
        return redirect(payment_session.url)


class PaymentSuccessView(View):
    template_name = 'payments/success.html'

    def get(self, request, *args, **kwargs):
        try:
            hash_ = request.GET['hash']
        except KeyError:
            raise PermissionDenied()
        try:
            payload = decode_jwt_signature(hash_)
        except (FatalSignatureError, SignatureExpiredError):
            raise PermissionDenied()

        price = Price.objects.get(id=payload.get('price_id'))
        return render(
            request,
            template_name=self.template_name,
            context={
                'price': price,
            }
        )
