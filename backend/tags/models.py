from django.db import models


class Tag(models.Model):
    tag_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(default='', blank=False, null=False)

    def __str__(self):
        return self.tag_name
