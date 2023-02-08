from django.urls import reverse
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import Answer, Choice, Question, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["label", "slug", "url"]
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
    class Meta:
        model = Choice
        fields = ["uuid", "question", "text", "is_correct"]
        extra_kwargs = {
            "question": {"view_name": "api:question-detail", "lookup_field": "uuid"},
        }


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    choices = ChoiceDetailSerializer(many=True)

    class Meta:
        model = Answer
        fields = ["url", "uuid", "user", "question", "choices", "is_correct"]
        extra_kwargs = {
            "url": {"view_name": "api:answer-detail", "lookup_field": "uuid"},
            "question": {"view_name": "api:question-detail", "lookup_field": "uuid"},
        }
