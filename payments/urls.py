from django.urls import path

from payments.views import (
    PaymentCallbackView,
    ProcessPaymentView,
    ProductsView,
)


app_name = 'payments'


urlpatterns = [
    path('<str:payment_hex>/process/', ProcessPaymentView.as_view(), name='process_payment'),
    path('products/', ProductsView.as_view(), name='products'),
    path('callbacks/<str:payment_status>/', PaymentCallbackView.as_view()),
]
