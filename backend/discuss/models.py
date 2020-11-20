from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from users.models import User, Vote
from tags.models import Tag


class Post(models.Model):
    score = models.PositiveIntegerField(default=0)
    content = models.TextField(blank=False, null=False)
    date_create = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-date_create']


class Question(Post):
    title = models.CharField(max_length=1000, blank=False, null=False)
    best_answer = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, related_name='question_list', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    @property
    def num_votes(self):
        return Vote.objects.filter(
                    object_id=self.id,
                    content_type=ContentType.objects.get_for_model(Question)
                ).count()


class Answer(Post):
    in_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    owner = models.ForeignKey(User, related_name='answer_list', on_delete=models.CASCADE)

    @property
    def num_votes(self):
        return Vote.objects.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(Answer)
        ).count()


class Comment(models.Model):
    content = models.TextField(blank=False, null=False)
    date_create = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    in_answer = models.ForeignKey(Answer, related_name='answer', on_delete=models.CASCADE)
