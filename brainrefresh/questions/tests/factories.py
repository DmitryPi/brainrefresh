from factory import Faker
from factory.django import DjangoModelFactory

from ..models import Tag


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    label = Faker("sentence", nb_words=3)
