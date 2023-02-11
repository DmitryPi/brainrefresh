from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from brainrefresh.users.tests.factories import SuperUserFactory, UserFactory

from ..api.serializers import QuestionDetailSerializer, QuestionListSerializer
from .factories import (
    AnswerFactory,
    ChoiceFactory,
    Question,
    QuestionFactory,
    TagFactory,
)

User = get_user_model()


class TagViewSetTests(APITestCase):
    def setUp(self):
        """
        TODO: test permissions
        """
        self.user = UserFactory()
        self.tag_1 = TagFactory(label="Test Tag 1")
        self.tag_2 = TagFactory(label="Test Tag 2")
        self.list_url = reverse("api:tag-list")
        self.detail_url = reverse("api:tag-detail", args=[self.tag_1.slug])

    def test_list(self):
        response = self.client.get(self.list_url)
        # test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_permissions_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_permissions_anon(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_caching(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.headers["Cache-Control"], "max-age=3600")

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        # test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "Test Tag 1")
        self.assertEqual(response.data["slug"], "test-tag-1")
        self.assertEqual(response.data["question_count"], 0)
        self.assertIn(self.detail_url, response.data["url"])

    def test_retrieve_permissions_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_permissions_anon(self):
        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_caching(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.headers["Cache-Control"], "max-age=3600")


class QuestionViewSetTests(APITestCase):
    def setUp(self):
        # Create a user to use for authentication
        self.user_log_pass = {"username": "testuser", "password": "testpassword"}
        self.user = UserFactory(**self.user_log_pass)
        # Create request factory
        self.factory = APIRequestFactory()
        # Create a client to make API requests
        self.client = APIClient()
        self.client.login(**self.user_log_pass)
        # Create some data for testing
        self.question_1 = QuestionFactory(
            title="What is your name?",
            published=True,
        )
        self.question_2 = QuestionFactory(
            title="What is your favorite color?",
            published=True,
        )
        self.question_3 = QuestionFactory(
            title="What is your favorite food?",
            published=False,
        )
        self.tag_1 = TagFactory(label="personal", slug="personal-1")
        self.tag_2 = TagFactory(label="favorites")
        self.question_1.tags.add(self.tag_1, self.tag_2)
        self.question_2.tags.add(self.tag_2)
        self.choice1 = ChoiceFactory(question=self.question_1, text="John")
        self.choice2 = ChoiceFactory(question=self.question_1, text="Jane")
        # urls
        self.list_url = reverse("api:question-list")
        self.detail_url = reverse(
            "api:question-detail", kwargs={"uuid": self.question_1.uuid}
        )
        # test question data
        self.q_data = {
            "user": self.user.pk,
            "title": "What is your address?",
            "tags": [
                {"slug": self.tag_1.slug},
                {"slug": self.tag_2.slug, "label": "123"},
            ],
        }
        self.q_data_1 = {
            "user": self.user.pk,
            "title": "What is your name?",
            "language": "RU",
        }

    def test_list(self):
        # Send a GET request to the list endpoint
        request = self.factory.get(self.list_url)
        response = self.client.get(self.list_url)
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the returned data is what we expect
        serializer = QuestionListSerializer(
            instance=Question.objects.published(),
            many=True,
            context={"request": request},
        )
        self.assertEqual(response.data, serializer.data)

    def test_list_permissions_anon(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        # Send a POST request to the create endpoint
        response = self.client.post(self.list_url, self.q_data, format="json")
        response_1 = self.client.post(self.list_url, self.q_data_1, format="json")
        # Check that the response has a status code of 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        # Check that the new question has been created in the database
        self.assertTrue(Question.objects.filter(title=self.q_data["title"]).exists())
        self.assertTrue(Question.objects.filter(title=self.q_data_1["title"]).exists())
        # Check that tags were added
        self.assertTrue(len(response.data["tags"]), 2)
        self.assertFalse(len(response_1.data["tags"]))

    def test_create_permissions_anon(self):
        self.client.logout()
        response = self.client.post(self.list_url, self.q_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        # Send a GET request to the retrieve endpoint for the first question
        request = self.factory.get(f"/api/questions/{self.question_1.uuid}/")
        response = self.client.get(f"/api/questions/{self.question_1.uuid}/")
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the returned data is what we expect
        serializer = QuestionDetailSerializer(
            instance=Question.objects.prefetch_related("tags", "choices")
            .published()
            .get(uuid=self.question_1.uuid),
            context={"request": request},
        )
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_permissions_anon(self):
        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        # Send a PUT request to the update endpoint for the first question
        data = {
            "user": self.user.pk,
            "title": "What is your age?",
            "text": "Must be a number",
            "explanation": "Amount of time that has passed since the birth of a person.",
            "tags": [
                {
                    "slug": self.tag_1.slug,
                }
            ],
        }
        response = self.client.put(self.detail_url, data, format="json")
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the question has been updated in the database
        self.question_1.refresh_from_db()
        self.assertEqual(self.question_1.title, data["title"])
        self.assertEqual(self.question_1.tags.count(), 1)

    def test_update_permissions_anon(self):
        self.client.logout()
        data = {"user": self.user.pk, "title": "What is your age?"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy(self):
        # Send a DELETE request to the destroy endpoint for the first question
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(uuid=self.question_1.uuid).exists())

    def test_destroy_anon(self):
        self.client.logout()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Question.objects.filter(uuid=self.question_1.uuid).exists())


class ChoiceViewSetTests(APITestCase):
    def setUp(self):
        # Create a Question and Choices mock data
        self.question = QuestionFactory(title="What is the meaning of life?")
        self.choices = [
            ChoiceFactory(
                question=self.question, text="To find happiness", is_correct=True
            ),
            ChoiceFactory(
                question=self.question, text="To serve others", is_correct=False
            ),
            ChoiceFactory(
                question=self.question, text="To seek knowledge", is_correct=False
            ),
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

    # def test_retrieve(self):
    #     # Get the URL for the ChoiceViewSet retrieve endpoint for the first choice
    #     url = reverse(
    #         "api:choice-detail",
    #         kwargs={
    #             "question_uuid": str(self.question.uuid),
    #             "uuid": str(self.choices[0].uuid),
    #         },
    #     )
    #     # Make a GET request to the endpoint
    #     response = self.client.get(url)
    #     # Assert that the response status code is 200 OK
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # Assert that the data returned in the response matches the data for the first choice
    #     self.assertEqual(response.data["text"], self.choices[0].text)

    # def test_create(self):
    #     # Create a new choice
    #     url = reverse(
    #         "api:choice-list", kwargs={"question_uuid": str(self.question.uuid)}
    #     )
    #     data = {
    #         "question": self.question.pk,
    #         "text": "A framework",
    #         "is_correct": False,
    #     }
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data["text"], data["text"])
    #     self.assertEqual(response.data["is_correct"], data["is_correct"])

    # def test_update(self):
    #     # Update an existing choice
    #     url = reverse(
    #         "api:choice-detail",
    #         kwargs={
    #             "question_uuid": str(self.question.uuid),
    #             "uuid": str(self.choices[0].uuid),
    #         },
    #     )
    #     data = {
    #         "question": self.question.pk,
    #         "text": "A language",
    #         "is_correct": False,
    #     }
    #     response = self.client.put(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["text"], data["text"])
    #     self.assertEqual(response.data["is_correct"], data["is_correct"])

    # def test_get_queryset(self):
    #     # Get the URL for the ChoiceViewSet retrieve endpoint for a choice with a non-existing UUID
    #     non_existing_uuid = str(uuid4())
    #     url = reverse(
    #         "api:choice-detail",
    #         kwargs={
    #             "question_uuid": str(self.question.uuid),
    #             "uuid": non_existing_uuid,
    #         },
    #     )
    #     # Make a GET request to the endpoint
    #     response = self.client.get(url)
    #     # Assert that the response status code is 404 Not Found
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AnswerViewSetTests(APITestCase):
    def setUp(self):
        # Create a user to use for authentication
        self.user_log_pass = {
            "username": "testuser",
            "password": "testpassword",
        }
        self.user = UserFactory(**self.user_log_pass)
        self.user_1 = SuperUserFactory()
        # Create Question
        self.question = QuestionFactory(
            title="What is Django?", text="Django is a high-level Python web framework"
        )
        # Create Choices
        self.choices = [
            ChoiceFactory(
                question=self.question, text="Python Framework", is_correct=True
            ),
            ChoiceFactory(
                question=self.question, text="Programming Language", is_correct=False
            ),
            ChoiceFactory(question=self.question, text="The Movie", is_correct=False),
        ]
        # Create Answers
        self.answers = [
            AnswerFactory(question=self.question, user=self.user, is_correct=True),
            AnswerFactory(question=self.question, user=self.user, is_correct=True),
            AnswerFactory(question=self.question, user=self.user_1, is_correct=True),
        ]
        # Create request factory
        self.factory = APIRequestFactory()
        self.answer_list_url = reverse("api:answer-list")
        self.answer_detail_url = reverse(
            "api:answer-detail", kwargs={"uuid": self.answers[0].uuid}
        )
        self.answer_detail_url_admin = reverse(
            "api:answer-detail", kwargs={"uuid": self.answers[2].uuid}
        )
        self.question_detail_url = reverse(
            "api:question-detail", kwargs={"uuid": self.question.uuid}
        )

    def test_list(self):
        # Test correct list of answers for request.user
        users = [
            {"instance": self.user, "answers_len": 2},
            {"instance": self.user_1, "answers_len": 1},
        ]
        for user in users:
            # Login user
            self.client.force_login(user["instance"])
            # Send a GET request to the list endpoint
            response = self.client.get(reverse("api:answer-list"))

            # Check that the response has a status code of 200 (OK)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Check that the returned data is what we expect
            self.assertEqual(len(response.data), user["answers_len"])

    def test_list_permissions_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.answer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_permissions_admin(self):
        self.client.force_login(self.user_1)
        response = self.client.get(self.answer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_permissions_anon(self):
        response = self.client.get(self.answer_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        # Login user
        self.client.force_login(self.user)
        # Build question hyperlink
        # question_url = self.factory.get(self.question_detail_url).build_absolute_uri()
        # Get API response
        response = self.client.get(self.answer_detail_url)
        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test serialized data
        self.assertEqual(response.data["uuid"], str(self.answers[0].uuid))
        self.assertEqual(response.data["question"], str(self.question.uuid))
        self.assertEqual(response.data["is_correct"], True)

    def test_retrieve_permissions_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.answer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_permissions_admin(self):
        self.client.force_login(self.user_1)
        response = self.client.get(self.answer_detail_url_admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_permissions_anon(self):
        response = self.client.get(self.answer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_create_answer(self):
    #     self.client.login(**self.user_log_pass)
    #     question_url = self.factory.get(self.question_detail_url).build_absolute_uri()
    #     data = {
    #         "question": self.question.uuid,
    #         "choices": [
    #             {
    #                 "uuid": self.choices[0].uuid,
    #                 "question": self.question.uuid,
    #                 "text": self.choices[0].text,
    #                 "is_correct": self.choices[0].is_correct,
    #             }
    #         ],
    #     }
    #     response = self.client.post("/api/answers/", data, format="json")
    #     self.assertEqual(response.content, "ABC")
    #     self.assertEqual(response.status_code, 201)

    # self.assertEqual(Answer.objects.count(), 1)
    # answer = Answer.objects.first()
    # self.assertEqual(answer.user, self.user)
    # self.assertEqual(answer.question, self.question)
    # self.assertEqual(answer.choices.count(), 1)
    # self.assertEqual(answer.choices.first(), self.choice)

    # def test_create(self):
    #     # Login user
    #     self.client.force_login(self.user)
    #     # Answer data
    #     question_url = self.factory.get(self.question_detail_url).build_absolute_uri()
    #     data = {
    #         "question": question_url,
    #         "choices": [
    #             {
    #                 "uuid": self.choices[0].uuid,
    #                 "question": question_url,
    #                 "text": "Раз",
    #                 "is_correct": True,
    #             },
    #         ],
    #         "is_correct": True,
    #     }
    #     response = self.client.post(self.answer_list_url, data)
    #     self.assertEqual(response.content, "ABC")

    # def test_create_anon(self):
    #     data = {"question": self.question.uuid}
    #     response = self.client.post(self.answer_list_url, data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
