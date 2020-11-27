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

import jwt

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import (status, permissions)
from rest_framework_simplejwt.tokens import RefreshToken

from . import serializers
from .utils import Util
from .models import User


class RegisterView(GenericAPIView):
    """
    Handle register request. Create new user and send an email to user's email
    if account don't exists. User must verify email to active account
    An error response is returned otherwise
    """
    serializer_class = serializers.RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # send an email to verify account
            user = serializer.save()

            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relative_link = reverse('users:email_verify')
            abs_url = 'http://'+current_site+relative_link+'?token='+str(token)
            body = 'Hi {username},\n\n' \
                   'Click here to verify your account: \n{link}\n\n' \
                   'Thanks,\n' \
                   'QandA-vietnam'.format(username=user.username, link=abs_url)
            Util.send_email(
                subject='QandA-vietnam Team - Confirm your email address',
                body=body,
                recipient_list=[user.email]
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    """
    This view will handle login request.
    A token will be returned if authen success
    """
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )


class EmailVerifyView(GenericAPIView):
    """
    Check token, if it valid, make user account activated
    """
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, key=settings.SIMPLE_JWT['SIGNING_KEY'])
            user = User.objects.get(pk=payload['user_id'])
            user.is_verified = True
            user.save()
            return Response(
                data={'message': 'Successfully activated'},
                status=status.HTTP_200_OK,
            )
        except jwt.ExpiredSignatureError:
            err_msg = 'Activation expired'
        except (ObjectDoesNotExist, jwt.exceptions.DecodeError):
            err_msg = 'Invalid token'

        return Response(
            data={'error': err_msg},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(GenericAPIView):
    """
    when user send a logout request, the refresh token must
    be saved to blacklist token (blacklist token contains
    tokens that no longer valid)
    """
    serializer_class = serializers.LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
