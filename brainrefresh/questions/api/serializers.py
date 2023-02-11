from django.shortcuts import get_object_or_404
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


class _QuestionChoiceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:choice-detail", lookup_field="uuid"
    )

    class Meta:
        model = Choice
        fields = [
            "url",
            "uuid",
            "text",
            "is_correct",
        ]
        extra_kwargs = {
            "is_correct": {"write_only": True},
        }


class QuestionDetailSerializer(QuestionBaseSerializer):
    choices = _QuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionBaseSerializer.Meta.model
        fields = QuestionBaseSerializer.Meta.fields + [
            "choices",
        ]

    def update(self, instance, validated_data):
        # pop tags
        tags_data = validated_data.pop("tags", [])
        tag_slugs = [tag["slug"] for tag in tags_data if "slug" in tag]
        # update question
        question = super().update(instance, validated_data)
        # filter tags by slugs
        tags = Tag.objects.filter(slug__in=tag_slugs)
        # set tags if any
        question.tags.set(tags)
        return question


class ChoiceSerializer(serializers.ModelSerializer):
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
