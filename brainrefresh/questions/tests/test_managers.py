from django.test import TestCase

from .factories import Question, QuestionFactory


class QuestionManagerTestCase(TestCase):
    def setUp(self):
        self.question1 = QuestionFactory(published=True)
        self.question2 = QuestionFactory(published=False)
        self.question3 = QuestionFactory(published=True)

    def test_published_manager(self):
        published_questions = Question.objects.published()
        self.assertEqual(len(published_questions), 2)
        self.assertIn(self.question1, published_questions)
        self.assertIn(self.question3, published_questions)
        self.assertNotIn(self.question2, published_questions)
