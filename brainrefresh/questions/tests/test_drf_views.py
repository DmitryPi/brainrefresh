from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .factories import TagFactory


class TagViewSetTestCase(APITestCase):
    def setUp(self):
        """
        TODO: test permissions
        """
        self.tag_1 = TagFactory(label="Test Tag 1")
        self.tag_2 = TagFactory(label="Test Tag 2")

    def test_list_tags(self):
        url = reverse("api:tag-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_tag(self):
        url = reverse("api:tag-detail", args=[self.tag_1.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "Test Tag 1")
        self.assertEqual(response.data["slug"], "test-tag-1")
