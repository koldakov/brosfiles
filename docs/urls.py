from django.urls import path

from docs.views import TermOfServicesView


app_name = 'docs'


urlpatterns = [
    path('terms/', TermOfServicesView.as_view(), name='terms_of_service'),
]
