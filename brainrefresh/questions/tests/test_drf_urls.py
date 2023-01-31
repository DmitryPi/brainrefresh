from django.urls import resolve, reverse

from ..models import Tag


def test_tag_list():
    assert reverse("api:tag-list") == "/api/tags/"
    assert resolve("/api/tags/").view_name == "api:tag-list"


def test_tag_detail(tag: Tag):
    assert (
        reverse("api:tag-detail", kwargs={"slug": tag.slug}) == f"/api/tags/{tag.slug}/"
    )
    assert resolve(f"/api/tags/{tag.slug}/").view_name == "api:tag-detail"
