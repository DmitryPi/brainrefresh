from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from .serializers import (
    ChoiceSerializer,
    Question,
    QuestionDetailSerializer,
    QuestionListSerializer,
    Tag,
    TagSerializer,
)
from .validators import UUID, validate_uuid


class TagViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "slug"
    permission_classes = ()


class QuestionViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    lookup_field = "uuid"
    permission_classes = ()

    def get_serializer_class(self):
        if self.action in ["retrieve", "update"]:
            return QuestionDetailSerializer
        return QuestionListSerializer

    def get_queryset(self):
        return Question.objects.prefetch_related("tags").published()


@extend_schema(
    parameters=[
        OpenApiParameter("question_uuid", UUID, OpenApiParameter.PATH),
        OpenApiParameter("uuid", UUID, OpenApiParameter.PATH),
    ]
)
class ChoiceViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = ChoiceSerializer
    lookup_field = "uuid"
    permission_classes = ()

    def get_queryset(self):
        question_uuid = self.kwargs.get("question_uuid")
        validate_uuid(question_uuid)
        question = get_object_or_404(
            Question.objects.select_related("question"), uuid=question_uuid
        )
        return question.choices.all()
