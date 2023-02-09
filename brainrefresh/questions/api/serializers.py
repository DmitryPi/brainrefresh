from django.shortcuts import get_object_or_404
from django.urls import reverse
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import Answer, Choice, Question, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["label", "slug", "question_count", "url"]
        extra_kwargs = {"url": {"view_name": "api:tag-detail", "lookup_field": "slug"}}


class TagSlugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["slug"]


class QuestionListSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Question
        fields = [
            "uuid",
            "user",
            "tags",
            "title",
            "language",
            "updated_at",
            "created_at",
            "url",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:question-detail", "lookup_field": "uuid"},
            "tags": {"view_name": "api:tag-detail", "lookup_field": "slug"},
        }


class QuestionDetailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = TagSerializer(many=True, read_only=True)
    choices_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "uuid",
            "user",
            "tags",
            "title",
            "text",
            "explanation",
            "language",
            "updated_at",
            "created_at",
            "choices_url",
        ]

    @extend_schema_field(str)
    def get_choices_url(self, obj):
        return self.context["request"].build_absolute_uri(
            reverse("api:choice-list", kwargs={"question_uuid": obj.uuid})
        )


class ChoiceListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["uuid", "question", "text", "is_correct", "url"]

    @extend_schema_field(str)
    def get_url(self, obj):
        rev = reverse(
            "api:choice-detail",
            kwargs={"question_uuid": obj.question.uuid, "uuid": obj.uuid},
        )
        return self.context.get("request").build_absolute_uri(rev)


class ChoiceDetailSerializer(serializers.HyperlinkedModelSerializer):
    question = serializers.HyperlinkedRelatedField(
        view_name="api:question-detail", lookup_field="uuid", read_only=True
    )

    class Meta:
        model = Choice
        fields = ["uuid", "question", "text", "is_correct"]


class _AnswerChoiceSerializer(serializers.ModelSerializer):
    """Used for serializing Answer model choices field"""

    question = serializers.UUIDField(source="question.uuid")

    class Meta:
        model = Choice
        fields = ["uuid", "question", "text", "is_correct"]


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    question = serializers.UUIDField(source="question.uuid")
    choices = _AnswerChoiceSerializer(many=True)

    class Meta:
        model = Answer
        fields = [
            "url",
            "uuid",
            "user",
            "question",
            "choices",
            "is_correct",
            "created_at",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:answer-detail", "lookup_field": "uuid"},
            "question": {"view_name": "api:question-detail", "lookup_field": "uuid"},
        }

    def create(self, validated_data):
        """
        TODO: nested creation
        """
        question_data = validated_data.pop("question")
        choices_data = validated_data.pop("choices")
        question = get_object_or_404(Answer, uuid=question_data["uuid"])
        answer = Answer.objects.create(question=question, **validated_data)
        for choice_data in choices_data:
            choice = get_object_or_404(Choice, uuid=choice_data["uuid"])
            answer.add(choice)
        return answer
