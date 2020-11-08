from django.contrib import admin
from users.models import User, Vote, Profile


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Vote)
