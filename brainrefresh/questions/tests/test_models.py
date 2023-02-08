from django.test import TestCase
from django.utils.text import slugify

from .factories import Tag, TagFactory


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
