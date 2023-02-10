from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import (
    Answer,
    AnswerSerializer,
    ChoiceDetailSerializer,
    ChoiceListSerializer,
    Question,
    QuestionDetailSerializer,
    QuestionListSerializer,
    Tag,
    TagSerializer,
)
from .validators import validate_uuid


class TagViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Tag.objects.prefetch_related("questions")
    serializer_class = TagSerializer
    lookup_field = "slug"
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(settings.API_CACHE_TIME))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(settings.API_CACHE_TIME))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class QuestionViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    lookup_field = "uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("language",)
    parameters = [
        OpenApiParameter(
            name="language",
            type=str,
            description="Filter by language (EN or RU)",
            required=False,
        ),
    ]

    def get_serializer_class(self):
        if self.action in ["retrieve", "update"]:
            return QuestionDetailSerializer
        return QuestionListSerializer

    def get_queryset(self):
        return Question.objects.prefetch_related("tags").published()


@extend_schema(
    parameters=[
        OpenApiParameter("question_uuid", OpenApiTypes.UUID, OpenApiParameter.PATH),
        OpenApiParameter("uuid", OpenApiTypes.UUID, OpenApiParameter.PATH),
    ]
)
class ChoiceViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    lookup_field = "uuid"
    permission_classes = ()

    def get_queryset(self):
        question_uuid = self.kwargs.get("question_uuid")
        validate_uuid(question_uuid)
        question = get_object_or_404(Question, uuid=question_uuid)
        return question.choices.all()

    def get_serializer_class(self):
        if self.action in ["retrieve", "update"]:
            return ChoiceDetailSerializer
        return ChoiceListSerializer


class AnswerViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = AnswerSerializer
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            Answer.objects.filter(user=self.request.user)
            .select_related("question")
            .prefetch_related("choices__question")
        )
        return queryset
