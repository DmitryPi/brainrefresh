from rest_framework import serializers

from ..models import Choice, Question, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["label", "slug", "url"]
        extra_kwargs = {"url": {"view_name": "api:tag-detail", "lookup_field": "slug"}}


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["uuid", "text", "is_correct"]


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "uuid",
            "tags",
            "title",
            "language",
            "updated_at",
            "created_at",
            "url",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:question-detail", "lookup_field": "uuid"}
        }


class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            "uuid",
            "user",
            "tags",
            "choices",
            "title",
            "text",
            "explanation",
            "language",
            "updated_at",
            "created_at",
            "url",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:question-detail", "lookup_field": "uuid"}
        }
