import datetime
import secrets
from typing import Type
from uuid import uuid4

from django.db import models
from django.utils.crypto import get_random_string

from accounts.exceptions import SafeRandomStringNotGenerated, UUID4HEXNotGenerated


def file_upload_path(instance: Type[models.Model], filename: str) -> str:
    """Generates file upload path.

    Args:
        instance (Type[models.Model): Instance with the ``django.db.models.FileField`` field.
        filename (str): Original file name.

    Returns:
        str: File upload path.
    """
    today = datetime.date.today()
    folders_structure = '%s/%s/%s' % (today.year, today.month, today.day)
    file_name = '%s_%s_%s' % (uuid4().hex, secrets.token_hex(nbytes=16), secrets.token_hex(nbytes=8))

    return 'data/files/%s/%s' % (folders_structure, file_name)


def get_uuid_hex(instance: Type[models.Model], field: str, tries: int = 5):
    """Generates UUID4 hex.

    Args:
        instance (models.Model): Instance to which create UUID4 hex.
        field (str): Field which needs UUID4 hex.
        tries (int, optional): Number of attempts to generate unique hex for given ``field``.

    Returns:
        str: UUID4 hex.

    Raises:
        accounts.exceptions.UUID4HEXNotGenerated: If hex is not generated.
    """
    for _ in range(tries):
        uuid4_hex = uuid4().hex

        try:
            instance.objects.get(**{field: uuid4_hex})
        except instance.DoesNotExist:
            return uuid4_hex
    else:
        raise UUID4HEXNotGenerated()


def get_safe_random_string(instance: Type[models.Model], field: str, tries: int = 5, length: int = 12):
    """Generates Safe random string.

    Args:
        instance (models.Model): Instance to which create safe random string.
        field (str): Field which needs safe random string.
        tries (int, optional): Number of attempts to generate unique string for given ``field``.
        length (int, optional): Length of the random string.

    Returns:
        str: Safe random string.

    Raises:
        accounts.exceptions.SafeRandomStringNotGenerated: If random string is not generated.
    """
    for _ in range(tries):
        uuid4_hex = get_random_string(length=length)

        try:
            instance.objects.get(**{field: uuid4_hex})
        except instance.DoesNotExist:
            return uuid4_hex
    else:
        raise SafeRandomStringNotGenerated()
