from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (User, Profile)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    User profile will be created immediately after user account is created
    """
    if created:
        Profile.objects.create(owner=instance)
