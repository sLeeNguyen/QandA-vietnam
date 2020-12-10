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

import logging
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from rest_framework import (status, permissions)
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView,
    DestroyAPIView, GenericAPIView
)
from rest_framework.response import Response
from rest_framework.utils import json

from . import serializers
from .models import (Question, Answer)
from tags.models import Tag
from .exceptions import FieldErrorException, ParamErrorException
from .permissions import IsOwner
from .pagination import ResultSetPagination
from .utils import strip_tags
from elasticsearch_client import elasticsearch

LOGGER = logging.getLogger(__name__)


class QuestionListView(ListAPIView):
    queryset = Question.objects.all()
    pagination_class = ResultSetPagination

    def get(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.filter_queryset(self.queryset))
        res = []
        if page is not None:
            for question in page:
                obj_dict = {
                    'id': question.id,
                    'title': question.title,
                    'content': question.short_content,
                    'date_create': question.date_create,
                    'score': question.score,
                    'best_answer': question.best_answer,
                    'num_of_votes': question.votes.all().count(),
                    'num_of_answers': question.answers.count(),
                    'owner': serializers.UserBasicInfoSerializer(
                        question.owner, context={'request': request}).data,
                    'tags': serializers.TagBasicInfoSerializer(
                        question.tags.all(), many=True).data
                }
                res.append(obj_dict)

        return self.get_paginated_response(res)

    def filter_queryset(self, queryset):
        """
        queryset will be sorted by date creation by default
        and filter with tags.
        """
        sort_field = self.request.GET.get("sort", "-date_create")
        filter_tags = self.request.GET.get("filter", "")

        queryset = queryset.order_by(sort_field)
        if filter_tags:
            tags = filter_tags.split(',')
            queryset = queryset.filter(tags__tag_name__in=tags)

        return queryset


class SearchView(ListAPIView):
    queryset = Question.objects.all()
    pagination_class = ResultSetPagination

    def get(self, request, *args, **kwargs):
        # print(request.META.get('HTTP_AUTHORIZATION', ''))
        data = self.get_data()
        self.count = data['hits']['total']['value']
        self.total_pages = self.count // self.paginator.page_size + 1

        if self.page_number > self.total_pages:
            return Response(status=status.HTTP_404_NOT_FOUND)

        res = []
        for element in data['hits']['hits']:
            if element['_index'] == "question":
                question = Question.objects.get(pk=element['_id'])
                content = element['highlight']['content'][0] if 'highlight' in element else question.short_content
                obj_dict = {
                    'id': question.id,
                    'title': question.title,
                    'content': content,
                    'date_create': question.date_create,
                    'score': question.score,
                    'best_answer': question.best_answer,
                    'num_of_votes': question.votes.all().count(),
                    'num_of_answers': question.answers.count(),
                    'owner': serializers.UserBasicInfoSerializer(
                        question.owner, context={'request': request}).data,
                    'tags': serializers.TagBasicInfoSerializer(
                        question.tags.all(), many=True).data
                }
            else:
                answer = Answer.objects.get(pk=element['_id'])
                content = element['highlight']['content'][0] if 'highlight' in element else answer.short_content
                obj_dict = {
                    'id': answer.id,
                    'content': content,
                    'date_create': answer.date_create,
                    'score': answer.score,
                    'num_of_votes': answer.votes.all().count(),
                    'owner': serializers.UserBasicInfoSerializer(
                        answer.owner, context={'request': request}).data,
                }
            res.append(obj_dict)

        return self.build_response(res)

    def get_data(self):
        search_query = self.request.query_params.get("q", "")
        self.sort = self.request.query_params.get("sort", "")
        tags = self.request.query_params.get("tags", "")
        if tags:
            tags = tags.split(",")
        else:
            tags = None

        return elasticsearch.discuss_search(query=search_query,
                                            start=self.get_start(),
                                            size=self.paginator.get_page_size(self.request),
                                            sort=self.sort,
                                            tags=tags)

    def get_start(self):
        paginator = self.paginator
        self.page_number = paginator.get_page_number(self.request)
        return (self.page_number - 1)*paginator.get_page_size(self.request)

    def build_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('total_pages', self.total_pages),
            ('current_page', self.page_number),
            ('results', data)
        ]))


class QuestionCreationView(CreateAPIView):
    serializer_class = serializers.QuestionCreationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        require_fields = ['title', 'content', 'tags']
        try:
            check_require_fields(require_fields, request.data.keys())
        except FieldErrorException as err:
            return Response(
                data={"error": err.__str__()},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Create an instance and save to elasticsearch.
        """
        tags = get_tag_by_list_tag_name(json.loads(self.request.data.get('tags')))
        instance = serializer.save(owner=self.request.user, tags=tags)
        content_strip_tags = strip_tags(instance.content)
        instance.short_content = content_strip_tags[:300]
        instance.save()
        info = elasticsearch.question_index(question_id=instance.id,
                                            title=instance.title,
                                            content=content_strip_tags,
                                            date_create=instance.date_create,
                                            tags=instance.get_list_tag_names(),
                                            owner_id=instance.owner.id)
        LOGGER.info(msg=info)


class QuestionDetailView(RetrieveAPIView):
    serializer_class = serializers.QuestionDetailSerializer
    queryset = Question.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, context={'request': request})
        res = serializer.data
        # get answer data for this question using answer serializer
        res['num_of_answers'] = instance.answers.count()
        res['answers'] = [
            serializers.AnswerDetailSerializer(
                answer,
                context={'request': request}).data for answer in instance.answers.all().order_by('date_create')
        ]

        return Response(res, status=status.HTTP_200_OK)


class QuestionUpdateDestroyView(UpdateAPIView, DestroyAPIView):
    serializer_class = serializers.QuestionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Question.objects.all()
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        require_fields = ['title', 'content', 'tags']
        try:
            check_require_fields(require_fields, request.data.keys())
        except FieldErrorException as err:
            return Response(
                data={"error": err.__str__()},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Update both instance in database and document in elasticsearch
        """
        tags = get_tag_by_list_tag_name(self.request.data.get('tags'))
        instance = serializer.save(tags=tags)
        info = elasticsearch.question_update(question_id=instance.id,
                                             title=instance.title,
                                             content=instance.content,
                                             tags=instance.get_list_tag_names())
        LOGGER.info(info)

    def perform_destroy(self, instance):
        """
        Delete both instance in database and document in elasticsearch
        """
        elasticsearch.question_delete(question_id=instance.id)
        instance.delete()


class AnswerCreationView(CreateAPIView):
    serializer_class = serializers.AnswerCreationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        require_fields = ['content', 'question_id']
        try:
            check_require_fields(require_fields, request.data.keys())
        except FieldErrorException as err:
            return Response(
                data={"error": err.__str__()},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        question = get_object_or_404(Question, pk=self.request.data.get('question_id'))
        instance = serializer.save(owner=self.request.user, in_question=question)
        info = elasticsearch.answer_index(answer_id=instance.id,
                                          content=strip_tags(instance.content),
                                          date_create=instance.date_create,
                                          owner_id=instance.owner.id)
        LOGGER.info(msg=info)


class AnswerListInQuestionView(ListAPIView):
    serializer_class = serializers.AnswerDetailSerializer
    pagination_class = ResultSetPagination
    queryset = Answer.objects.all()
    lookup_field = 'id'  # this is question_id that answers belong to

    def filter_queryset(self, queryset):
        """
        queryset will be sorted by param in request url
        (sort by 'score' in descending order, by default)
        and filtered with question own question_id.
        """
        sorted_field = self.request.GET.get('answertab', '-score')
        queryset = queryset.filter(in_question=self.get_object()).order_by(sorted_field)
        return queryset

    def get_object(self):
        """
        Return the question object with id in request url.
        """
        question_id = self.kwargs[self.lookup_field]
        return get_object_or_404(Question, pk=question_id)


class AnswerUpdateDestroyView(UpdateAPIView, DestroyAPIView):
    serializer_class = serializers.AnswerDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Answer.objects.all()
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        require_fields = ['content']
        try:
            check_require_fields(require_fields, request.data.keys())
        except FieldErrorException as err:
            return Response(
                data={"error": err.__str__()},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Update both instance in database and document in elasticsearch
        """
        instance = serializer.save()
        info = elasticsearch.answer_update(answer_id=instance.id,
                                           content=instance.content)
        LOGGER.info(msg=info)

    def perform_destroy(self, instance):
        """
        Delete both instance in database and document in elasticsearch
        """
        elasticsearch.answer_delete(answer_id=instance.id)
        instance.delete()


class VoteView(GenericAPIView):
    lookup_field = 'id'
    obj_type_field = 'type'  # type of voted object, value {'answer', 'question'}
    vote_action_filed = 'action'  # up vote or down vote, value {'up', 'down'}
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            self._check_params()
        except ParamErrorException as e:
            return Response(data={'error': e.__str__()},
                            status=status.HTTP_400_BAD_REQUEST)

        post = self.get_object()
        owner_of_post = post.owner
        points = self._get_points()
        user = request.user

        vote = user.votes.get(post=post)
        if not vote.exists():
            post.score += points['post_point']
            owner_of_post.profile.reputation_score += points['user_points']
            if owner_of_post.profile.reputation_score < 0:
                owner_of_post.profile.reputation_score = 0

            post.save()
            owner_of_post.profile.save()
            user.vote(post=post, vote_type=self.vote_action)

        else:
            # check if vote action is difference
            # reset post's score and user's reputation_score
            # update with new points
            vote = vote[0]
            if vote.type != self.vote_action:
                post.score += 2 * points['post_point']
                owner_of_post.profile.reputation_score += 2 * points['user_points']
                if owner_of_post.profile.reputation_score < 0:
                    owner_of_post.profile.reputation_score = 0
                vote.type = self.vote_action

                post.save()
                owner_of_post.profile.save()
                vote.save()

        res = {
            'post': {
                'id': post.id,
                'new_score': post.score
            },
            'action': self.vote_action
        }
        return Response(data=res, status=status.HTTP_200_OK)

    def get_queryset(self):
        if self.obj_type == 'question':
            queryset = Question.objects.all()
        else:
            queryset = Answer.objects.all()
        return queryset

    def _get_points(self, ):
        if self.vote_action == 'up':
            return {
                'user_points': 10,
                'post_point': 1
            }
        else:
            return {
                'user_points': -10,
                'post_point': -1
            }

    def _check_params(self):
        self.obj_type = self.kwargs[self.obj_type_field].lower()
        self.vote_action = self.kwargs[self.vote_action_filed].lower()
        if self.obj_type not in ['question', 'answer']:
            error_msg = "Got unexpect object type '%s'. " \
                        "It must be set to 'question' or 'answer'" % self.obj_type
            raise ParamErrorException(error_msg)

        if self.vote_action not in ['up', 'down']:
            error_msg = "Got unexpect vote action '%s'. " \
                        "It must be set to 'up' or 'down'" % self.vote_action
            raise ParamErrorException(error_msg)


def check_require_fields(require_fields, request_data_keys):
    lack_fields = []
    for field in require_fields:
        if field not in request_data_keys:
            lack_fields.append(field)
    if lack_fields:
        raise FieldErrorException(
            "Require field(s): \'%s\'." % (', '.join(lack_fields))
        )


def get_tag_by_list_tag_name(list_tag_names):
    """
    List Tag objects are queried by tag_name in request.data.
    """
    tag_objs = []
    if list_tag_names:
        for tag_name in list_tag_names:
            try:
                tag_objs.append(Tag.objects.get(tag_name=tag_name))
            except ObjectDoesNotExist:
                pass
    return tag_objs
