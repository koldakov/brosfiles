from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.utils import get_uuid_hex


def get_message_hex():
    """Generates UUID4 hex for message."""
    return get_uuid_hex(Message, "hex")


class Message(models.Model):
    hex = models.CharField(
        _("Message hex"),
        max_length=32,
        default=get_message_hex,
        editable=False,
        null=False,
        blank=False,
        unique=True
    )
    text = models.TextField(
        _("Message text"),
        editable=False,
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(
        _("Created date"),
        default=timezone.now
    )
