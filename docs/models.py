from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TermsOfService(models.Model):
    version = models.IntegerField(
        _('Version'),
        null=False,
        blank=False
    )
    date_created = models.DateTimeField(
        _('Date created'),
        default=timezone.now
    )
    reference = models.CharField(
        _('Reference'),
        max_length=32,
        null=False,
        blank=False
    )

    class Meta:
        get_latest_by = ['date_created']
