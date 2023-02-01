from django.urls import resolve, reverse

from ..models import Question, Tag


def test_tag_list():
    assert reverse("api:tag-list") == "/api/tags/"
    assert resolve("/api/tags/").view_name == "api:tag-list"


def test_tag_detail(tag: Tag):
    assert (
        reverse("api:tag-detail", kwargs={"slug": tag.slug}) == f"/api/tags/{tag.slug}/"
    )
    assert resolve(f"/api/tags/{tag.slug}/").view_name == "api:tag-detail"


def test_question_list():
    assert reverse("api:question-list") == "/api/questions/"
    assert resolve("/api/questions/").view_name == "api:question-list"


def test_question_detail(question: Question):
    rev = reverse("api:question-detail", kwargs={"uuid": question.uuid})
    res = resolve(f"/api/questions/{question.uuid}/").view_name
    assert rev == f"/api/questions/{question.uuid}/"
    assert res == "api:question-detail"
