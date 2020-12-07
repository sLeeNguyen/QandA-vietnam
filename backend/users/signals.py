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

import random

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
        avt_default = 'avt/avatar-%s.png' % str(random.randint(1, 8))
        Profile.objects.create(owner=instance, display_name=instance.username, avatar=avt_default)
