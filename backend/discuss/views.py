from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import (
    GenericAPIView, CreateAPIView, ListAPIView, RetrieveAPIView)
from rest_framework.response import Response
from rest_framework import (status, permissions)

from . import serializers
from .models import (Question, Answer)
from tags.models import Tag
from .exceptions import FieldErrorException


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
                    'owner': serializers.UserBasicInfoSerializer(question.owner).data,
                    'tags': serializers.TagBasicInfoSerializer(question.tags.all(), many=True).data
                }
                res.append(obj_dict)

        return Response(
            data=res,
            status=status.HTTP_200_OK
        )

    def filter_queryset(self, queryset):
        """
        Filter queryset by parameters in request.GET
        queryset will be sorted by date creation by default
        """
        sort_field = self.request.GET.get("sort", "-date_create")
        filter_tags = self.request.GET.get("filter", "")

        queryset = queryset.order_by(sort_field)
        print(filter_tags)
        if filter_tags:
            tags = filter_tags.split(',')
            queryset = queryset.filter(tags__tag_name__in=tags)

        return queryset


class QuestionSearchView(ListAPIView):
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
        tags = self._get_tags()
        serializer.save(owner=self.request.user, tags=tags)

    def _get_tags(self):
        """
        :returns: list Tag objects are queried by tag_name in request.data
        """
        tag_list = self.request.data.get('tags', [])
        tag_objs = []
        if tag_list:
            for tag_name in tag_list:
                try:
                    tag_objs.append(Tag.objects.get(tag_name=tag_name))
                except ObjectDoesNotExist:
                    pass
        return tag_objs


class QuestionDetailView(RetrieveAPIView):
    serializer_class = serializers.QuestionDetailSerializer
    queryset = Question.objects.all()
    lookup_field = 'id'


class AnswerCreationView(CreateAPIView):
    serializer_class = serializers.AnswerCreationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Question.objects.all()
    lookup_field = 'id'  # the question_id

    def post(self, request, *args, **kwargs):
        require_fields = ['content']
        try:
            check_require_fields(require_fields, request.data.keys())
        except FieldErrorException as err:
            return Response(
                data={"error": err.__str__()},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        question = self.get_object()
        serializer.save(owner=self.request.user, in_question=question)


def check_require_fields(require_fields, request_data_keys):
    for field in require_fields:
        if field not in request_data_keys:
            raise FieldErrorException(
                "Field \'%s\' is required" % field
            )
