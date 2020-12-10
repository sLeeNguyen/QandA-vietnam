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

from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.models import ContentType

from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(UserManager):
    use_in_migrations = True

    def find_by_username(self, username):
        query_set = self.get_queryset()
        return query_set.filter(username=username)

    def find_by_email(self, email):
        query_set = self.get_queryset()
        return query_set.filter(email=email)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Users within the Django authentication system are represented by this
    model.

    Username, email and password are required. Other fields are optional.
    """
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.CharField(max_length=150, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def __str__(self):
        return self.username

    def vote(self, post, vote_type):
        content_type = ContentType.objects.get_for_model(post)

        return Vote.objects.create(
            user=self,
            content_type=content_type,
            object_id=post.id,
            type=vote_type
        )


class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(default='', blank=True)
    reputation_score = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='avt/', default='avt/default-avt.png')
