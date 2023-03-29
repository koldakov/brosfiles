from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductBase(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=128,
        editable=True,
        null=False,
        blank=False
    )
    description = models.TextField(
        _('Description'),
        editable=True,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        _('Price'),
        max_digits=16,
        decimal_places=2,
        editable=True,
        null=True,
        blank=True
    )
    sku = models.CharField(
        _('SKU'),
        max_length=16,
        editable=True,
        null=True,
        blank=True
    )
    currency = models.CharField(
        _('Currency'),
        max_length=8,
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
        ordering = ['id']

    def get_internal_info(self, user):
        raise NotImplementedError()


class Subscription(ProductBase):
    DEFAULT_MAX_STORAGE_SIZE: int = 2147483648  # 2 * 2 ^ 30 = 2 GB
    DEFAULT_MAX_FILE_SIZE: int = 209715200  # Maximum file size200 * 2 ^ 20 = 200 MB

    max_file_size = models.PositiveBigIntegerField(
        _('Maximum file size'),
        default=DEFAULT_MAX_FILE_SIZE,
        null=True,
        blank=True
    )
    storage_size = models.PositiveBigIntegerField(
        _('Storage size'),
        default=DEFAULT_MAX_STORAGE_SIZE,
        null=True,
        blank=True
    )

    def get_internal_info(self, user):
        msg: str = _('Product is available!')
        is_available: bool = True
        is_current: bool = False

        return {
            'is_available': is_available,
            'message': msg,
            'is_current': is_current,
        }
