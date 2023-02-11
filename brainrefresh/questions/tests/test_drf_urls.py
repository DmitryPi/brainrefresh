from django.urls import resolve, reverse

from ..models import Answer, Choice, Question, Tag


def test_tag_list():
    assert reverse("api:tag-list") == "/api/tags/"
    assert resolve("/api/tags/").view_name == "api:tag-list"


def test_tag_detail(tag: Tag):
    url = f"/api/tags/{tag.slug}/"
    assert reverse("api:tag-detail", kwargs={"slug": tag.slug}) == url
    assert resolve(url).view_name == "api:tag-detail"


def test_question_list():
    assert reverse("api:question-list") == "/api/questions/"
    assert resolve("/api/questions/").view_name == "api:question-list"


def test_question_detail(question: Question):
    url = f"/api/questions/{question.uuid}/"
    assert reverse("api:question-detail", kwargs={"uuid": question.uuid}) == url
    assert resolve(url).view_name == "api:question-detail"


def test_choice_list():
    url = "/api/choices/"
    assert reverse("api:choice-list") == url
    assert resolve(url).view_name == "api:choice-list"


def test_choice_detail(choice: Choice):
    url = f"/api/choices/{choice.uuid}/"
    assert reverse("api:choice-detail", kwargs={"uuid": choice.uuid}) == url
    assert resolve(url).view_name == "api:choice-detail"


def test_answer_list():
    assert reverse("api:answer-list") == "/api/answers/"
    assert resolve("/api/answers/").view_name == "api:answer-list"


def test_answer_detail(answer: Answer):
    url = f"/api/answers/{answer.uuid}/"
    assert reverse("api:answer-detail", kwargs={"uuid": answer.uuid}) == url
    assert resolve(url).view_name == "api:answer-detail"
