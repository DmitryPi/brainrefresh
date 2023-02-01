import pytest

from brainrefresh.questions.tests.factories import (
    Choice,
    ChoiceFactory,
    Question,
    QuestionFactory,
    Tag,
    TagFactory,
)
from brainrefresh.users.models import User
from brainrefresh.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def tag(db) -> Tag:
    return TagFactory()


@pytest.fixture
def question(db) -> Question:
    return QuestionFactory()


@pytest.fixture
def choice(db) -> Choice:
    return ChoiceFactory()
