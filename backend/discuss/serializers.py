from rest_framework import serializers

from .models import (Question, Answer)
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


class AnswerCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['content']

    def to_representation(self, instance):
        return {
            'question_id': instance.in_question.id,
            'answer': AnswerDetailSerializer(instance).data
        }


class AnswerDetailSerializer(serializers.ModelSerializer):
    owner = UserBasicInfoSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'content', 'score', 'date_create', 'last_update', 'owner'
        ]


class QuestionCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['title', 'content']


class QuestionDetailSerializer(serializers.ModelSerializer):
    answers = AnswerDetailSerializer(many=True, read_only=True)
    owner = UserBasicInfoSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
