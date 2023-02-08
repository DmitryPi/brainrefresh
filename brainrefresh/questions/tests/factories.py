from collections.abc import Sequence
from typing import Any

from factory import Faker, SubFactory, post_generation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from brainrefresh.users.tests.factories import UserFactory

from ..models import Answer, Choice, Question, Tag


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    label = Faker("sentence", nb_words=3)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    user = SubFactory(UserFactory)
    title = Faker("sentence", nb_words=4)
    text = Faker("text")
    explanation = Faker("text")
    language = FuzzyChoice([Question.Lang.EN])
    published = FuzzyChoice([True, False])

    @post_generation
    def tags(self, create: bool, extracted: Sequence[Any], **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of tags were passed in, use them
            for tag in extracted:
                self.tags.add(tag)
        else:
            size = 4
            for _ in range(size):
                tag = TagFactory()
                self.tags.add(tag)


class ChoiceFactory(DjangoModelFactory):
    class Meta:
        model = Choice

    question = SubFactory(QuestionFactory)
    text = Faker("text")
    is_correct = FuzzyChoice([True, False])


class AnswerFactory(DjangoModelFactory):
    class Meta:
        model = Answer

    user = SubFactory(UserFactory)
    question = SubFactory(QuestionFactory)
    is_correct = FuzzyChoice([True, False])

    @post_generation
    def choices(self, create: bool, extracted: Sequence[Any], **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of choices were passed in, use them
            for choice in extracted:
                self.choices.add(choice)
        else:
            size = 2
            for _ in range(size):
                choice = ChoiceFactory()
                self.choices.add(choice)
