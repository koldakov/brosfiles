from django.contrib import admin

from docs.models import TermsOfService


@admin.register(TermsOfService)
class TermsOfServiceAdmin(admin.ModelAdmin):
    pass
