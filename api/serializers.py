from django.contrib.auth.models import update_last_login
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from accounts.models import User
from api.exceptions import UserAlreadyExists


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'is_active',
        ]
        read_only_field = ['is_active']


class SignInSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class SignUpSerializer(UserSerializer):
    username = serializers.CharField(
        max_length=64,
        min_length=3,
        write_only=True,
        required=True
    )
    first_name = serializers.CharField(
        max_length=150,
        min_length=3
    )
    last_name = serializers.CharField(
        max_length=50,
        min_length=3
    )
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True
    )
    email = serializers.EmailField(
        max_length=254,
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email',
            'first_name', 'last_name', 'is_active',
        ]

    def create(self, validated_data):
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError:
            raise UserAlreadyExists()
