import logging

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from rest_framework import (status, permissions)
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
)
from rest_framework.response import Response

from . import serializers
from .models import (Question, Answer)
from tags.models import Tag
from .exceptions import FieldErrorException
from .permissions import IsOwner
from .pagination import AnswerResultSetPagination
from .utils import strip_tags
from elasticsearch_client import elasticsearch

LOGGER = logging.getLogger(__name__)


class QuestionListView(ListAPIView):
    queryset = Question.objects.all()

    def get(self, request):
        page = self.paginate_queryset(self.filter_queryset(self.queryset))
        res = []
        if page is not None:
            for question in page:
                obj_dict = {
                    'id': question.id,
                    'title': question.title,
                    'content': question.content,
                    'date_create': question.date_create,
                    'score': question.score,
                    'num_of_votes': question.num_votes,
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
    pass


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
        tags = get_tag_by_list_tag_name(self.request.data.get('tags'))
        instance = serializer.save(owner=self.request.user, tags=tags)
        info = elasticsearch.question_index(question_id=instance.id,
                                            title=instance.title,
                                            content=strip_tags(instance.content),
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
        res['answers'] = [
            serializers.AnswerDetailSerializer(
                answer, context={'request': request}).data for answer in instance.answers.all()
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


class AnswerListView(ListAPIView):
    serializer_class = serializers.AnswerDetailSerializer
    pagination_class = AnswerResultSetPagination
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
