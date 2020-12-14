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
from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

from .models import (Question, Answer, Vote, Comment)
from tags.serializers import TagSerializer
from users.models import User
from tags.models import Tag


class UserBasicInfoSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='profile.display_name', read_only=True)
    reputation_score = serializers.IntegerField(source='profile.reputation_score', read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'display_name', 'reputation_score', 'avatar'
        ]


class TagBasicInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'tag_name']


class CommentDetailSerializer(serializers.ModelSerializer):
    owner = UserBasicInfoSerializer(read_only=True)

    class Meta:
        model = Comment
        exclude = ['in_post']


class CommentCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['content']

    def to_representation(self, instance):
        return {
            'post_id': instance.in_post.id,
            'comment': CommentDetailSerializer(instance, context=self.context).data
        }


class AnswerCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['content']

    def to_representation(self, instance):
        return {
            'question_id': instance.in_question.id,
            'answer': AnswerDetailSerializer(instance, context=self.context).data
        }


class AnswerDetailSerializer(serializers.ModelSerializer):
    owner = UserBasicInfoSerializer(read_only=True)
    comments = CommentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'content', 'score', 'date_create', 'last_update', 'owner', 'comments'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        data['num_of_comments'] = len(data['comments'])
        data['comments'] = data['comments'][:5]
        if type(user) == AnonymousUser:
            data['voted'] = 0
            data['is_owner'] = 0
            return data

        if instance.owner.id == user.id:
            data['is_owner'] = 1

        vote = user.votes.filter(post=instance)
        if vote.exists():
            vote = vote[0]
            if vote.type == Vote.UP_VOTE:
                data['voted'] = 1
            else:
                data['voted'] = -1
        else:
            data['voted'] = 0
        return data


class QuestionCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['title', 'content']

    def to_representation(self, instance):
        return QuestionDetailSerializer(instance, context=self.context).data


class QuestionDetailSerializer(serializers.ModelSerializer):
    owner = UserBasicInfoSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['num_of_comments'] = len(data['comments'])
        data['comments'] = data['comments'][:5]
        user = self.context['request'].user

        if type(user) == AnonymousUser:
            data['voted'] = 0
            data['is_owner'] = 0
            return data

        if instance.owner.id == user.id:
            data['is_owner'] = 1

        vote = user.votes.filter(post=instance)
        if vote.exists():
            vote = vote[0]
            if vote.type == Vote.UP_VOTE:
                data['voted'] = 1
            else:
                data['voted'] = -1
        else:
            data['voted'] = 0
        return data


class QuestionContentSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']

    def to_representation(self, instance):
        tags = ' '.join([tag.tag_name for tag in instance.tags.all()])
        return {
            'title': instance.title,
            'content': instance.content,
            'tags': tags,
        }


class AnswerContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['content']
