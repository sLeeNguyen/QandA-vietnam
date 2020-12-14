# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#     Copyright 2020 QandA-vietnam.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User, Profile


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
    token = serializers.DictField(read_only=True)
    display_name = serializers.CharField(max_length=150, read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'token', 'display_name', 'avatar']
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
            raise AuthenticationFailed('Tài khoản hoặc mật khẩu không chính xác')
        if not user.is_active:
            raise AuthenticationFailed('Tài khoản bị khoá')
        if not user.is_verified:
            raise AuthenticationFailed('Tài khoản chưa được kích hoạt')

        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'display_name': user.profile.display_name,
            'avatar': user.profile.avatar,
            'token': user.tokens,
        }

    def to_representation(self, instance):
        return {
            'user': {
                'id': instance['id'],
                'username': instance['username'],
                'display_name': instance['display_name'],
                'email': instance['email'],
                'avatar_url': self.context['request'].build_absolute_uri(instance['avatar'].url)
            },
            'token': instance['token']
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


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions', 'last_login']

    def to_representation(self, instance):
        pass


