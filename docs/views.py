from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import Http404
from django.shortcuts import render
from django.views import View

from docs.models import TermsOfService


class TermOfServicesView(View):
    template_name = 'docs/terms_of_service.html'

    def get(self, request, *args, **kwargs):
        try:
            terms = TermsOfService.objects.latest()
        except TermsOfService.DoesNotExist:
            raise Http404()

        with staticfiles_storage.open('docs/terms_of_service_%s_en.txt' % terms.version) as terms_file:
            terms_text = terms_file.read().decode()

        return render(
            request=request,
            template_name=self.template_name,
            context={
                'terms_of_service': terms,
                'terms_text': terms_text
            }
        )
