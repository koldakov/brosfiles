from hashlib import sha256
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.db import models
from django.db.models.fields.files import FieldFile
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import magic

from accounts.dataclasses import SignedURLReturnObject
from accounts.enums import SignedURLMethod
from accounts.managers import UserManager
from accounts.utils import file_upload_path, get_safe_random_string, get_uuid_hex
from docs.models import TermsOfService


MAGIC_MIME = magic.Magic(mime=True)
DEFAULT_MAX_FILE_SIZE: int = 209715200  # Maximum file size200 * 2 ^ 20 = 200 MB
DEFAULT_STORAGE_SIZE: int = 2147483648  # 2 * 2 ^ 30 = 2 GB
MIN_FILE_SIZE: int = 0


class UserDoesNotHaveSubscription(Exception):
    """User does not have subscription."""


class MetadataFieldDoesNotExist(Exception):
    """Field of the metadata does not exist."""


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
    terms_of_service = models.ForeignKey(
        TermsOfService,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    psp_reference = models.CharField(
        _('PSP ID'),
        max_length=32,
        editable=False,
        null=True,
        blank=True
    )
    psp_id = models.CharField(
        _('PSP ID'),
        max_length=32,
        editable=False,
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
        """Retrieves maximum upload file size.

        Each ``payments.models.Subscription`` has a ``payments.models.Product``, each product has
        metadata field and max_file_size inside it.
        If the  user bought a subscription this value will be returned and
        ``self.max_file_size`` otherwise.

        Return:
            int: Maximum upload file size.
        """
        try:
            # That's a difficult operation.
            # TODO: Caching.
            metadata = self.subscriptions.filter(active=True).latest('id').product.metadata
        except ObjectDoesNotExist:
            return self.max_file_size
        try:
            max_file_size = metadata['max_file_size']
        except KeyError:
            return self.max_file_size
        try:
            return int(max_file_size)
        except (ValueError, TypeError):
            return self.max_file_size

    def get_subscription_metadata(self):
        """Gets metadata for the subscription.

        In theory, we can get not the latest subscriptions, but get subscriptions with maximum
        storage size and max upload file size, but for now that's fine.
        Plus I have not decided how to handle multiple subscriptions and if we need them at all.

        Returns:
            django.db.models.JSONField: If user has an active subscription.

        Raises:
            accounts.models.UserDoesNotHaveSubscription: If user does not have an active subscription.
        """
        try:
            # That's a difficult operation.
            # TODO: Caching.
            return self.subscriptions.filter(active=True).latest('id').product.metadata
        except ObjectDoesNotExist:
            raise UserDoesNotHaveSubscription()

    def get_used_storage(self):
        space = self.files.exclude(size=None).values_list('size', flat=True).aggregate(used_storage=models.Sum('size'))
        return space['used_storage'] or 0

    def is_file_size_allowed(self, file_size: int):
        try:
            metadata = self.get_subscription_metadata()
        except UserDoesNotHaveSubscription:
            metadata = dict(storage_size=DEFAULT_STORAGE_SIZE)
        storage_size = int(metadata['storage_size'])
        return file_size + self.get_used_storage() < storage_size

    def configure_from_event(self, event):
        if event.data.object.customer:
            self.psp_id = event.data.object.customer
            self.save(update_fields=['psp_id'])


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
