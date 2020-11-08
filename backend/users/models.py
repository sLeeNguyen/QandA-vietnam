from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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

    def __str__(self):
        return self.username

    def get_display_name(self):
        if self.profile.display_name:
            return self.profile.display_name
        return self.username

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(default='', blank=True)
    reputation_score = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='avt/', default='avt/default-avt.png')


class Vote(models.Model):
    VOTE_CHOICES = [
        ('up', _('up vote')),
        ('down', _('down vote')),
    ]
    date_vote = models.DateTimeField(timezone.now)
    type = models.CharField(max_length=4, blank=False, null=False, choices=VOTE_CHOICES)
    user = models.ForeignKey(User, related_name='votes', on_delete=models.CASCADE)
