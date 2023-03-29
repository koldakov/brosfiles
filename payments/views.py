from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from payments.models import Subscription


class ProductsView(View):
    template_name = 'accounts/products.html'

    def get(self, request, *args, **kwargs):
        # TODO: Don't do like this
        products = Subscription.objects.all()

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
            product = Subscription.objects.get(id=product_id)
        except Subscription.DoesNotExist:
            raise PermissionDenied()

        raise PermissionDenied()


class ProcessPaymentView(LoginRequiredMixin, View):
    template_name = 'accounts/payment.html'

    def get(self, request, *args, **kwargs):
        raise PermissionDenied()

    def post(self, request, *args, **kwargs):
        raise PermissionDenied()


class PaymentCallbackView(LoginRequiredMixin, View):
    template_name = 'accounts/callbacks/payment.html'

    def get(self, request, *args, **kwargs):
        raise PermissionDenied()
