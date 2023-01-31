from rest_framework import serializers

from ..models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["label", "slug", "url"]
        extra_kwargs = {"url": {"view_name": "api:tag-detail", "lookup_field": "slug"}}
