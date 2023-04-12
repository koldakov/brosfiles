from enum import EnumMeta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class EnumField(serializers.Field):
    def __init__(self, **kwargs):
        self.enum = kwargs.pop('enum')
        super().__init__()
        if not isinstance(self.enum, EnumMeta):
            msg = 'Incorrect type. Expected an Enum, but got %s.'
            raise RuntimeError(msg % type(self.enum).__name__)

    def to_representation(self, value):
        return value.value

    def to_internal_value(self, data):
        try:
            return self.enum[data]
        except KeyError:
            raise ValidationError('%s not supported value' % data)
