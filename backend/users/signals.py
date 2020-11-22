from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (User, Profile)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    User profile will be created immediately after user account is created.\n
    display_name field will be set to username by default
    """
    if created:
        Profile.objects.create(owner=instance, display_name=instance.username)
