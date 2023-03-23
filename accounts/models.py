from hashlib import sha256
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import models
from django.db.models.fields.files import FieldFile
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import magic
from payments import PaymentStatus
from payments.models import BasePayment

from accounts.dataclasses import SignedURLReturnObject
from accounts.enums import SignedURLMethod
from accounts.managers import UserManager
from accounts.utils import file_upload_path, get_safe_random_string, get_uuid_hex
from docs.models import TermsOfService


MAGIC_MIME = magic.Magic(mime=True)
DEFAULT_MAX_FILE_SIZE: int = 209715200  # Maximum file size200 * 2 ^ 20 = 200 MB
DEFAULT_MAX_STORAGE_SIZE: int = 2147483648  # 2 * 2 ^ 30 = 2 GB
MIN_FILE_SIZE: int = 0


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=64,
        help_text=_('150 characters or fewer. Letters and digits only.'),
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
        null=False,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        _('First name'),
        max_length=150,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=50,
        null=False,
        blank=False
    )
    email = models.EmailField(
        _('Email address'),
        max_length=254,
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
        default=None,
        null=False,
        blank=False,
        unique=True
    )
    is_staff = models.BooleanField(
        _('Staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.'),
    )
    date_joined = models.DateTimeField(
        _('Date joined'),
        default=timezone.now
    )
    public_key = models.TextField(
        _('Public key'),
        max_length=2056,
        null=True,
        blank=True
    )
    max_file_size = models.IntegerField(
        _('Maximum file size'),
        default=DEFAULT_MAX_FILE_SIZE,
        null=True,
        blank=True
    )
    subscription = models.ForeignKey(
        'accounts.Subscription',
        related_name='clients',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    terms_of_service = models.ForeignKey(
        TermsOfService,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self) -> str:
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'

        if self.first_name:
            return self.first_name

        if self.last_name:
            return self.last_name

        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs) -> None:
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_max_file_size(self):
        if self.subscription is None:
            return self.max_file_size

        return self.subscription.max_file_size


def get_upload_hex():
    """Generates UUID4 hex for upload_hex field."""
    return get_uuid_hex(File, 'upload_hex')


def get_url_path():
    """Generates unique hash for file."""
    return '%s' % get_safe_random_string(File, 'url_path')


class File(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True
    )
    file = models.FileField(
        _('File'),
        max_length=512,
        upload_to=file_upload_path,
        null=True,
        blank=True
    )
    sha256 = models.CharField(
        _('File sha256 hash'),
        max_length=64,
        editable=False,
        null=False,
        blank=False
    )
    original_full_name = models.CharField(
        _('Original full name'),
        max_length=256,
        editable=False,
        null=False,
        blank=False
    )
    original_name = models.CharField(
        _('Original name'),
        max_length=128,
        editable=False,
        null=True,
        blank=True
    )
    original_extension = models.CharField(
        _('Original extension'),
        max_length=64,
        editable=False,
        null=True,
        blank=True
    )
    content_type = models.CharField(
        _('Content type'),
        max_length=128,
        editable=False,
        null=False,
        blank=False
    )
    is_private = models.BooleanField(
        _('Is private'),
        default=False
    )
    is_encrypted = models.BooleanField(
        _('Is encrypted'),
        editable=False,
        default=False
    )
    size = models.IntegerField(
        _('Size'),
        editable=False,
        null=True,
        blank=True
    )
    exif = models.TextField(
        _('Exif data'),
        max_length=65535,
        editable=False,
        null=True,
        blank=True
    )
    ip = models.CharField(
        _('IP'),
        max_length=16,
        editable=False,
        null=False,
        blank=False
    )
    upload_hex = models.CharField(
        _('Upload hex'),
        max_length=32,
        default=get_upload_hex,
        editable=False,
        null=False,
        blank=False,
        unique=True
    )
    url_path = models.CharField(
        _('URL Path'),
        max_length=64,
        default=get_url_path,
        editable=False,
        null=False,
        blank=False,
        unique=True
    )
    date_uploaded = models.DateTimeField(
        _('Uploaded date'),
        default=timezone.now
    )

    DEFAULT_SIGNED_URL_EXPIRATION = 15 * 60
    MIN_SIGNED_URL_EXPIRATION = 0
    MAX_SIGNED_URL_EXPIRATION = 7 * 24 * 60 * 60
    SUPPORTED_METHODS = (
        SignedURLMethod.PUT,
        SignedURLMethod.GET,
    )

    def __str__(self):
        return self.sha256[:8]

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        ordering = ['-id']

    def save(self, *args, **kwargs):
        fake: bool = kwargs.pop('fake', False)
        original_full_name: str = kwargs.pop('original_full_name', None)

        self.set_name_attrs(original_full_name)

        if fake is False:
            self.set_file_attrs()
        else:
            self.set_fake_file_attrs()

        super().save(*args, **kwargs)

    def set_name_attrs(self, original_full_name):
        if self.original_full_name and original_full_name is None:
            return

        if original_full_name is not None:
            self.original_full_name = original_full_name
        else:
            self.original_full_name = self.file.name

        # Avoid using absolute paths, because absolute paths can be not supported by backends.
        file_path = Path(self.original_full_name)

        self.original_name = file_path.stem
        self.original_extension = file_path.suffix

        if not self.original_name:
            self.original_name = None

        if not self.original_extension:
            self.original_extension = None

    def set_fake_file_attrs(self):
        self.sha256 = 'fake'
        self.size = None
        self.content_type = ''

    def set_file_attrs(self):
        sha256sum = sha256()

        for idx, chunk in enumerate(self.file.chunks()):
            if idx == 0:
                self.content_type = File.get_content_type_from_buffer(chunk)

            sha256sum.update(chunk)

        self.sha256 = sha256sum.hexdigest()
        # File size is not limited, it will be limited on upload.
        self.size = self.file.size

    @staticmethod
    def get_content_type_from_buffer(chunk: bytes):
        """Returns content type from buffer.

        Args:
            chunk (bytes): First chunk of the file.

        Note:
            First chunk - 65536 bytes is enough to determine the content type. There is no need to pass the whole file.

        Returns:
            str: The content type of the given chunk.
        """
        try:
            mime_type = MAGIC_MIME.from_buffer(chunk)
        except IsADirectoryError:
            mime_type = 'inode/directory'
        except (TypeError, SyntaxError):
            mime_type = 'application/unknown'

        return mime_type

    def get_signed_url_expiration(self, expiration: Optional[int]) -> int:
        """Returns expiration time of the signed URL.

        Args:
            expiration (int, optional): Expiration time in seconds or None.
                If specified must be greater than 0 and less than 60*60*24*7 (7 days).
                If not specified, then ``File.DEFAULT_SIGNED_URL_EXPIRATION`` will be used.

        Returns:
            int: Expiration time of the signed URL in seconds.

        Raises:
            ValueError: If wrong expiration time is specified.
        """
        if expiration is None:
            return self.DEFAULT_SIGNED_URL_EXPIRATION

        if self.MIN_SIGNED_URL_EXPIRATION > expiration > self.MAX_SIGNED_URL_EXPIRATION:
            raise ValueError(
                'Wrong expiration time; min=%s, max=%s' % (
                    self.MIN_SIGNED_URL_EXPIRATION,
                    self.MAX_SIGNED_URL_EXPIRATION
                )
            )

        return expiration

    def generate_upload_signed_url(
            self,
            expiration: Optional[int] = None,
            headers: Optional[dict] = None
    ) -> SignedURLReturnObject:
        """Generates upload signed URL depending on storage.

        Note:
            If ``expiration`` is not specified expiration time will be ``File.DEFAULT_SIGNED_URL_EXPIRATION``.

        Args:
            expiration (int, optional): Expiration time in seconds or None.
                If specified must be greater than 0 and less than 60*60*24*7 (7 days).
                If not specified, then ``File.DEFAULT_SIGNED_URL_EXPIRATION`` will be used.
            headers (dict, optional): Extra headers.

        Returns:
            accounts.dataclasses.SignedURLReturnObject: Values that allows clients to make upload request.

        Raises:
            NotImplementedError: If storage is not supported.
        """
        raise NotImplementedError()

    def generate_post_upload_signed_url(
            self,
            expiration: Optional[int] = None,
            headers: Optional[dict] = None
            ) -> SignedURLReturnObject:
        if expiration is None:
            expiration = self.get_signed_url_expiration(expiration)

        presigned_post = self.file.field.storage.connection.meta.client.generate_presigned_post(
            Bucket=self.file.storage.bucket_name,
            Key=self.file.name,
            Conditions=[
                ["content-length-range", MIN_FILE_SIZE, self.get_max_file_size()],
                {"bucket": self.file.storage.bucket_name},
            ],
            ExpiresIn=expiration,
        )

        return SignedURLReturnObject(
            url=presigned_post['url'],
            headers={},
            method=SignedURLMethod.POST.value,
            body=dict(presigned_post['fields'].items())
        )

    def generate_download_signed_url(
            self,
            expiration: Optional[int] = None,
            headers: Optional[dict] = None
    ) -> SignedURLReturnObject:
        """Generates download signed URL depending on storage.

        Note:
            If ``expiration`` is not specified expiration time will be ``File.DEFAULT_SIGNED_URL_EXPIRATION``.

        Args:
            expiration (int, optional): Expiration time in seconds or None.
                If specified must be greater than 0 and less than 60*60*24*7 (7 days).
                If not specified, then ``File.DEFAULT_SIGNED_URL_EXPIRATION`` will be used.
            headers (dict, optional): Extra headers.

        Returns:
            accounts.dataclasses.SignedURLReturnObject: Values that allows clients to make upload request.

        Raises:
            NotImplementedError: If storage is not supported.
        """
        expiration: int = self.get_signed_url_expiration(expiration)

        if settings.AWS_STORAGE_BUCKET_NAME:
            return self.generate_aws_s3_download_signed_url(expiration=expiration, headers=headers)

        raise NotImplementedError()

    def generate_aws_s3_download_signed_url(self, expiration=None, headers=None):
        """Generates AWS S3 download signed URL.

        Args:
            expiration (int, optional): Expiration time in seconds.
                If specified must be greater than 0 and less than 60*60*24*7 (7 days).
                If not specified, then ``File.DEFAULT_SIGNED_URL_EXPIRATION`` will be used.
            headers (dict, optional): Extra headers.

        Returns:
            accounts.dataclasses.SignedURLReturnObject: Values that allows clients to download the file.
        """
        expiration: int = self.get_signed_url_expiration(expiration)
        method: str = SignedURLMethod.GET.value

        if headers is None:
            headers = {}

        url = self.file.storage.url(
            self.file.name,
            parameters={
                'ResponseContentDisposition': 'attachment; filename ="%s";' % self.original_full_name,
            },
            expire=expiration,
            http_method=method
        )

        return SignedURLReturnObject(
            url=url,
            headers=headers,
            method=method,
            body={}
        )

    def get_h_size(self):
        """Returns humanreadable size of the file.

        Returns:
            str: Human readable size.
        """
        return filesizeformat(self.size)

    def is_user_has_access(self, user: User):
        if self.owner is None:
            return True

        if not self.is_private:
            return True

        return self.owner == user

    def get_max_file_size(self):
        if self.owner is None:
            return DEFAULT_MAX_FILE_SIZE

        return self.owner.get_max_file_size()

    @staticmethod
    def get_user_file_by_url_path(user: User, url_path):
        try:
            file = File.objects.get(url_path=url_path)
        except File.DoesNotExist:
            raise PermissionDenied()

        if file.is_user_has_access(user):
            return file

        raise PermissionDenied()

    def has_delete_permission(self, user: User):
        if self.owner is None:
            return False

        return self.owner == user


def generate_fake_file(original_name, owner: User = None, is_private: bool = True):
    file = File()

    file_field = models.FileField(upload_to=file_upload_path(File, original_name), name=original_name)
    field_file = FieldFile(field=file_field, name=file_field.upload_to, instance=models.FileField)

    file.owner = owner
    file.is_private = is_private
    file.file = field_file
    file.save(fake=True, original_full_name=original_name)

    return file


class ProductItemPoint(models.Model):
    short_description = models.CharField(
        _('Short description'),
        max_length=128,
        editable=True,
        null=False,
        blank=False
    )
    description = models.TextField(
        _('Description'),
        editable=True,
        null=False,
        blank=False
    )


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
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE
    )
    item_points = models.ManyToManyField(
        ProductItemPoint,
        blank=True
    )

    def get_internal_info(self, user: User):
        raise NotImplementedError()

    class Meta:
        abstract = True
        ordering = ['id']


class Subscription(ProductBase):
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

    def get_internal_info(self, user: User):
        msg: str = _('Product is available!')
        is_available: bool = True
        is_current: bool = False

        if user.is_anonymous:
            return {
                'is_available': is_available,
                'message': msg,
                'is_current': is_current,
            }

        if self == user.subscription:
            msg = _('This product already yours!')
            is_available = False
            is_current = True
        elif self.has_purchased_parent(self.parent, user.subscription):
            msg = _('You have much advanced subscription!')
            is_available = False

        return {
            'is_available': is_available,
            'message': msg,
            'is_current': is_current,
        }

    def has_purchased_parent(self, parent_subscription, current_subscription, depth=20):
        if parent_subscription is None:
            return False

        if parent_subscription == current_subscription:
            return True

        depth -= 1

        if depth == 0:
            raise RecursionError('Max depth in product inheritance')

        return self.has_purchased_parent(parent_subscription.parent, current_subscription, depth=depth)


def get_payment_hex():
    """Generates UUID4 hex for payment_hex field."""
    return get_uuid_hex(Payment, 'payment_hex')


class Payment(BasePayment):
    payment_hex = models.CharField(
        _('Payment hex'),
        max_length=32,
        default=get_payment_hex,
        editable=False,
        null=False,
        blank=False,
        unique=True
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        null=False,
        blank=False
    )
    product = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        null=False,
        blank=False
    )

    def get_failure_url(self) -> str:
        return 'https://%s/accounts/callbacks/failure/?ph=%s' % (settings.PAYMENT_HOST, self.payment_hex)

    def get_success_url(self) -> str:
        return 'https://%s/accounts/callbacks/success/?ph=%s' % (settings.PAYMENT_HOST, self.payment_hex)

    def configure_user(self):
        if self.status != PaymentStatus.CONFIRMED:
            return

        self.client.subscription = self.product

        self.client.save()
