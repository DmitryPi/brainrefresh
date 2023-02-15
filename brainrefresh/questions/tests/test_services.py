import pytest

from ..services import check_question_is_multichoice
from .factories import ChoiceFactory, QuestionFactory


@pytest.mark.django_db
def test_check_question_is_multichoice_true():
    question = QuestionFactory()
    ChoiceFactory.create_batch(2, question=question, is_correct=False)
    ChoiceFactory.create_batch(2, question=question, is_correct=True)
    result = check_question_is_multichoice(question)
    # Test result
    assert isinstance(result, bool)
    assert result


@pytest.mark.django_db
def test_check_question_is_multichoice_false():
    question = QuestionFactory()
    ChoiceFactory.create_batch(2, question=question, is_correct=False)
    ChoiceFactory.create_batch(1, question=question, is_correct=True)
    result = check_question_is_multichoice(question)
    # Test result
    assert isinstance(result, bool)
    assert not result
