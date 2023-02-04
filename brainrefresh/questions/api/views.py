from django.shortcuts import get_object_or_404
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
from .validators import validate_uuid


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
        question = get_object_or_404(Question, uuid=question_uuid)
        return question.choices.all()
