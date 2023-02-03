from rest_framework import serializers

from ..models import Choice, Question, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["label", "slug", "url"]
        extra_kwargs = {"url": {"view_name": "api:tag-detail", "lookup_field": "slug"}}


class QuestionListSerializer(serializers.ModelSerializer):
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
            "url": {"view_name": "api:question-detail", "lookup_field": "uuid"}
        }


class QuestionDetailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

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
            "url",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:question-detail", "lookup_field": "uuid"}
        }


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["uuid", "question", "text", "is_correct"]
