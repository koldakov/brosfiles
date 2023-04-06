from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentications import StripeAuthentication
from api.v1.services import StripeWebhookService


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(APIView):
    authentication_classes = (StripeAuthentication,)

    def post(self, request, *args, **kwargs):
        service = StripeWebhookService(request.auth)
        service.process_post_request()

        return Response(status=status.HTTP_200_OK)
