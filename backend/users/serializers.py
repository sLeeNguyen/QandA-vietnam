from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )


class LoginSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token']
        extra_kwargs = {
            'email': {'validators': []},
            'username': {'read_only': True},
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials. Please try again')
        if not user.is_active:
            raise AuthenticationFailed('Account is blocked')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'username': user.username,
            'email': user.email,
            'token': user.tokens,
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_messages = {
        'bad_token': _('Token is expired or invalid'),
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh', '')
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(token=self.token).blacklist()
        except TokenError:
            self.fail('bad_token')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
