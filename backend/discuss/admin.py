from django.contrib import admin
from discuss import models


admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.QuestionTag)
admin.site.register(models.Comment)
