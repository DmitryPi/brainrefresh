from django.shortcuts import get_object_or_404
from django.urls import reverse
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import Answer, Choice, Question, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["url", "label", "slug", "question_count"]
        extra_kwargs = {"url": {"view_name": "api:tag-detail", "lookup_field": "slug"}}


class _QuestionTagSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:tag-detail", lookup_field="slug"
    )
    label = serializers.CharField(read_only=True)
    slug = serializers.SlugField()


class QuestionBaseSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:question-detail", lookup_field="uuid"
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = _QuestionTagSerializer(Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Question
        fields = [
            "url",
            "uuid",
            "user",
            "title",
            "text",
            "explanation",
            "language",
            "updated_at",
            "created_at",
            "tags",
        ]


class QuestionListSerializer(QuestionBaseSerializer):
    class Meta:
        model = QuestionBaseSerializer.Meta.model
        fields = QuestionBaseSerializer.Meta.fields
        extra_kwargs = {
            "text": {"write_only": True},
            "explanation": {"write_only": True},
        }

    def create(self, validated_data):
        # pop tags
        tags_data = validated_data.pop("tags", [])
        tag_slugs = [tag["slug"] for tag in tags_data if "slug" in tag]
        # create question, filter tags by slugs
        question = Question.objects.create(**validated_data)
        tags = Tag.objects.filter(slug__in=tag_slugs)
        # set tags if any
        question.tags.set(tags)
        return question


class QuestionDetailSerializer(QuestionBaseSerializer):
    choices_url = serializers.SerializerMethodField()

    class Meta:
        model = QuestionBaseSerializer.Meta.model
        fields = [
            "choices_url",
        ] + QuestionBaseSerializer.Meta.fields

    @extend_schema_field(str)
    def get_choices_url(self, obj):
        return self.context["request"].build_absolute_uri(
            reverse("api:choice-list", kwargs={"question_uuid": obj.uuid})
        )

    def update(self, instance, validated_data):
        # pop tags
        tags_data = validated_data.pop("tags", [])
        print(tags_data)
        tag_slugs = [tag["slug"] for tag in tags_data if "slug" in tag]
        # update question
        question = super().update(instance, validated_data)
        # filter tags by slugs
        tags = Tag.objects.filter(slug__in=tag_slugs)
        # set tags if any
        question.tags.set(tags)
        return question


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
