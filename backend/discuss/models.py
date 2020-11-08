from django.db import models
from django.utils import timezone

from users.models import User
from tags.models import Tag


class Post(models.Model):
    class Meta:
        abstract = True

    score = models.PositiveIntegerField(default=0)
    content = models.TextField(blank=False, null=False)
    date_create = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField(blank=True, null=True)


class Question(Post):
    title = models.CharField(max_length=1000 ,blank=False, null=False)
    best_answer = models.PositiveIntegerField(default=0)


class Answer(Post):
    in_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')


class QuestionTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='tags')


class Comment(models.Model):
    content = models.TextField(blank=False, null=False)
    date_create = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    in_answer = models.ForeignKey(Answer, related_name='answer', on_delete=models.CASCADE)
