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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import User
from tags.models import Tag


class Post(models.Model):
    score = models.IntegerField(default=0)
    content = models.TextField(blank=False, null=False)
    short_content = models.TextField(blank=False, null=False)
    date_create = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    @property
    def num_votes(self):
        return Vote.objects.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(Question)
        ).count()

    class Meta:
        ordering = ['-date_create']


class Question(Post):
    title = models.CharField(max_length=1000, blank=False, null=False)
    best_answer = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, related_name='question_list', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    def get_list_tag_names(self):
        return [tag.tag_name for tag in self.tags.all()]


class Answer(Post):
    in_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    owner = models.ForeignKey(User, related_name='answer_list', on_delete=models.CASCADE)


class Comment(models.Model):
    content = models.TextField(blank=False, null=False)
    date_create = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    in_post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)


class Vote(models.Model):
    UP_VOTE = 'up'
    DOWN_VOTE = 'down'
    VOTE_CHOICES = [
        (UP_VOTE, _('up vote')),
        (DOWN_VOTE, _('down vote')),
    ]
    date_vote = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=4, blank=False, null=False, choices=VOTE_CHOICES)
    user = models.ForeignKey(User, related_name='votes', on_delete=models.CASCADE)
    post = models.ForeignKey(to=Post, related_name="votes", on_delete=models.CASCADE)
