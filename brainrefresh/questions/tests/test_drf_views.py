from uuid import uuid4

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from ..api.serializers import QuestionDetailSerializer, QuestionListSerializer
from .factories import ChoiceFactory, Question, QuestionFactory, TagFactory

User = get_user_model()


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


class QuestionViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a user to use for authentication
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        # Create request factory
        self.factory = APIRequestFactory()
        # Create a client to make API requests
        self.client = APIClient()
        self.client.login(username="testuser", password="testpassword")

        # Create some data for testing
        self.question1 = QuestionFactory(
            title="What is your name?",
            published=True,
        )
        self.question2 = QuestionFactory(
            title="What is your favorite color?",
            published=True,
        )
        self.question3 = QuestionFactory(
            title="What is your favorite food?",
            published=False,
        )
        self.tag1 = TagFactory(label="personal")
        self.tag2 = TagFactory(label="favorites")
        self.question1.tags.add(self.tag1, self.tag2)
        self.question2.tags.add(self.tag2)
        self.choice1 = ChoiceFactory(question=self.question1, text="John")
        self.choice2 = ChoiceFactory(question=self.question1, text="Jane")

    def test_list_questions(self):
        # Send a GET request to the list endpoint
        request = self.factory.get("/api/questions/")
        response = self.client.get("/api/questions/")

        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the returned data is what we expect
        serializer = QuestionListSerializer(
            instance=Question.objects.published(),
            many=True,
            context={"request": request},
        )
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_question(self):
        # Send a GET request to the retrieve endpoint for the first question
        request = self.factory.get(f"/api/questions/{self.question1.uuid}/")
        response = self.client.get(f"/api/questions/{self.question1.uuid}/")

        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the returned data is what we expect
        serializer = QuestionDetailSerializer(
            instance=Question.objects.prefetch_related("tags", "choices")
            .published()
            .get(uuid=self.question1.uuid),
            context={"request": request},
        )
        self.assertEqual(response.data, serializer.data)

    def test_update_question(self):
        # Send a PUT request to the update endpoint for the first question
        response = self.client.put(
            f"/api/questions/{self.question1.uuid}/",
            data={"user": self.user.pk, "title": "What is your age?"},
        )

        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the question has been updated in the database
        self.question1.refresh_from_db()
        self.assertEqual(self.question1.title, "What is your age?")

    def test_create_question(self):
        # Send a POST request to the create endpoint
        response = self.client.post(
            "/api/questions/",
            data={
                "user": self.user.pk,
                "title": "What is your address?",
                "is_published": True,
            },
        )

        # Check that the response has a status code of 201 (Created)
        self.assertEqual(response.status_code, 201)

        # Check that the new question has been created in the database
        self.assertTrue(Question.objects.filter(title="What is your address?").exists())


class ChoiceViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a Question object
        self.question = QuestionFactory(title="What is the meaning of life?")
        # Create some Choice objects associated with the Question
        self.choice_1 = ChoiceFactory(
            question=self.question, text="To find happiness", is_correct=True
        )
        self.choice_2 = ChoiceFactory(
            question=self.question, text="To serve others", is_correct=False
        )
        self.choice_3 = ChoiceFactory(
            question=self.question, text="To seek knowledge", is_correct=False
        )
        # Create a question and choices for testing
        self.question_1 = QuestionFactory(text="What is Python?")
        self.choices = [
            ChoiceFactory(text="A language", question=self.question_1, is_correct=True),
            ChoiceFactory(text="A snake", question=self.question_1, is_correct=False),
        ]

    def test_list(self):
        # Get the URL for the ChoiceViewSet list endpoint
        url = reverse(
            "api:choice-list", kwargs={"question_uuid": str(self.question.uuid)}
        )
        # Make a GET request to the endpoint
        response = self.client.get(url)
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the number of choices returned in the response is the same as the number of choices created
        self.assertEqual(len(response.data), 3)

    def test_retrieve(self):
        # Get the URL for the ChoiceViewSet retrieve endpoint for the first choice
        url = reverse(
            "api:choice-detail",
            kwargs={
                "question_uuid": str(self.question.uuid),
                "uuid": str(self.choice_1.uuid),
            },
        )
        # Make a GET request to the endpoint
        response = self.client.get(url)
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the data returned in the response matches the data for the first choice
        self.assertEqual(response.data["text"], self.choice_1.text)

    def test_create(self):
        # Create a new choice
        url = reverse(
            "api:choice-list", kwargs={"question_uuid": str(self.question_1.uuid)}
        )
        data = {
            "question": self.question_1.pk,
            "text": "A framework",
            "is_correct": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], data["text"])
        self.assertEqual(response.data["is_correct"], data["is_correct"])

    def test_update(self):
        # Update an existing choice
        choice = self.choices[0]
        url = reverse(
            "api:choice-detail",
            kwargs={
                "question_uuid": str(self.question_1.uuid),
                "uuid": str(choice.uuid),
            },
        )
        data = {
            "question": self.question_1.pk,
            "text": "A language",
            "is_correct": False,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], data["text"])
        self.assertEqual(response.data["is_correct"], data["is_correct"])

    def test_get_queryset(self):
        # Get the URL for the ChoiceViewSet retrieve endpoint for a choice with a non-existing UUID
        non_existing_uuid = str(uuid4())
        url = reverse(
            "api:choice-detail",
            kwargs={
                "question_uuid": str(self.question.uuid),
                "uuid": non_existing_uuid,
            },
        )
        # Make a GET request to the endpoint
        response = self.client.get(url)
        # Assert that the response status code is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
