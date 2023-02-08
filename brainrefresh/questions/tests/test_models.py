from uuid import UUID

from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from brainrefresh.users.tests.factories import UserFactory

from .factories import Question, QuestionFactory, Tag, TagFactory


class TagTests(TestCase):
    def setUp(self):
        self.tag_data = {"label": "test tag"}
        self.tag_slug = slugify(self.tag_data["label"])
        self.tag = TagFactory(label=self.tag_data["label"])

    def test_create(self):
        tag = TagFactory(**self.tag_data)
        self.assertEqual(tag.label, self.tag_data["label"])

    def test_read(self):
        tag = TagFactory(**self.tag_data)
        read_tag = Tag.objects.get(id=tag.id)
        self.assertEqual(read_tag.label, self.tag_data["label"])

    def test_update(self):
        new_label = "Updated Test Tag"
        tag = TagFactory(**self.tag_data)
        tag.label = new_label
        tag.save()
        updated_tag = Tag.objects.get(id=tag.id)
        self.assertEqual(updated_tag.label, new_label)

    def test_delete(self):
        tag = TagFactory(**self.tag_data)
        tag.delete()
        with self.assertRaises(Tag.DoesNotExist):
            Tag.objects.get(id=tag.id)

    def test_str(self):
        self.assertEqual(str(self.tag), self.tag_data["label"])

    def test_slug_generation(self):
        self.assertTrue(self.tag.slug)

    def test_slug_uniqueness(self):
        new_tag = TagFactory(label=self.tag_data["label"])
        self.assertNotEqual(self.tag.slug, new_tag.slug)
        self.assertTrue(f"{self.tag_slug}-1" in new_tag.slug)

    def test_label_change_updates_slug(self):
        previous_slug = self.tag.slug
        self.tag.label = "updated label"
        self.tag.save()
        self.assertNotEqual(previous_slug, self.tag.slug)

    def test_label_change_doesnt_update_slug_if_unmodified(self):
        previous_slug = self.tag.slug
        self.tag.save()
        self.assertEqual(previous_slug, self.tag.slug)


class QuestionTests(TestCase):
    def setUp(self):
        self.user = UserFactory(username="testuser", password="12345")
        self.tag = TagFactory(label="test_tag")
        self.question = QuestionFactory(
            user=self.user,
            title="Test Question Title",
            text="Test Question Text",
            explanation="Test explanation",
            language=Question.Lang.EN,
            published=True,
        )

    def test_create(self):
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(self.question.title, "Test Question Title")
        self.assertEqual(self.question.text, "Test Question Text")
        self.assertEqual(self.question.explanation, "Test explanation")
        self.assertEqual(self.question.language, Question.Lang.EN)
        self.assertTrue(self.question.published)

    def test_update(self):
        self.question.title = "Updated test question"
        self.question.save()
        self.question.refresh_from_db()
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(self.question.title, "Updated test question")
        self.assertEqual(self.question.text, "Test Question Text")
        self.assertEqual(self.question.explanation, "Test explanation")
        self.assertEqual(self.question.language, Question.Lang.EN)
        self.assertTrue(self.question.published)

    def test_delete(self):
        self.question.delete()
        self.assertEqual(Question.objects.count(), 0)

    def test_str(self):
        self.assertEqual(str(self.question), "Test Question Title")

    def test_fields(self):
        self.question.tags.add(self.tag)
        self.question.refresh_from_db()
        # assert fields are correctly saved and retrieved
        self.assertEqual(self.question.user, self.user)
        self.assertEqual(self.question.title, "Test Question Title")
        self.assertEqual(self.question.text, "Test Question Text")
        self.assertEqual(self.question.language, Question.Lang.EN)
        self.assertEqual(self.question.published, True)
        self.assertIsInstance(self.question.uuid, UUID)
        self.assertIsInstance(self.question.created_at, timezone.datetime)
        self.assertIsInstance(self.question.updated_at, timezone.datetime)
        self.assertIn(self.tag, self.question.tags.all())
