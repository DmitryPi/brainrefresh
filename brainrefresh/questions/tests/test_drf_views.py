from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from brainrefresh.users.tests.factories import SuperUserFactory, UserFactory

from ..api.serializers import QuestionDetailSerializer, QuestionListSerializer
from .factories import (
    AnswerFactory,
    Choice,
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

    def test_list_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_anon(self):
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

    def test_retrieve_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_anon(self):
        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_caching(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.headers["Cache-Control"], "max-age=3600")


class QuestionViewSetTests(APITestCase):
    def setUp(self):
        # Create a users to use for authentication
        self.user = UserFactory()
        self.user_1 = UserFactory()
        self.user_admin = SuperUserFactory()
        # Create request factory
        self.factory = APIRequestFactory()
        # Create a client to make API requests
        self.client = APIClient()
        # Create some data for testing
        self.question_1 = QuestionFactory(
            user=self.user,
            title="What is your name?",
            published=True,
        )
        self.question_2 = QuestionFactory(
            user=self.user,
            title="What is your favorite color?",
            published=True,
        )
        self.question_3 = QuestionFactory(
            user=self.user,
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
            "title": "What is your address?",
            "tags": [
                {"slug": self.tag_1.slug},
                {"slug": self.tag_2.slug, "label": "123"},
            ],
        }
        self.q_data_1 = {
            "title": "What is your name?",
            "language": "RU",
        }
        self.q_update_data = {
            "title": "What is your age?",
            "text": "Must be a number",
            "explanation": "Amount of time that has passed since the birth of a person.",
            "tags": [
                {
                    "slug": self.tag_1.slug,
                }
            ],
        }

    def test_list(self):
        self.client.force_login(self.user)
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
        self.assertEqual(response.data["results"], serializer.data)

    def test_list_anon(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_pagination(self):
        response = self.client.get(self.list_url)
        response_keys = list(response.data.keys())
        keys = ["limit", "offset", "count", "next", "previous", "results"]
        # Test response
        self.assertEqual(response_keys, keys)
        self.assertTrue(response.data["count"], 2)

    def test_create(self):
        self.client.force_login(self.user)
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

    def test_create_anon(self):
        self.client.logout()
        response = self.client.post(self.list_url, self.q_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        self.client.force_login(self.user)
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

    def test_retrieve_anon(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.force_login(self.user)
        # Send a PUT request to the update endpoint for the first question
        response = self.client.put(self.detail_url, self.q_update_data, format="json")
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the question has been updated in the database
        self.question_1.refresh_from_db()
        self.assertEqual(self.question_1.title, self.q_update_data["title"])
        self.assertEqual(self.question_1.tags.count(), 1)

    def test_update_anon(self):
        data = {"user": self.user.pk, "title": "What is your age?"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_for_other_users(self):
        self.client.force_login(self.user_admin)
        # Send a PUT request to the update endpoint for the first question
        response = self.client.put(self.detail_url, self.q_update_data, format="json")
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the question has been updated in the database
        self.question_1.refresh_from_db()
        self.assertEqual(self.question_1.title, self.q_update_data["title"])
        self.assertEqual(self.question_1.tags.count(), 1)

    def test_user_cant_update_for_other_users(self):
        self.client.force_login(self.user_1)
        # Send a PUT request to the update endpoint for the first question
        response = self.client.put(self.detail_url, self.q_update_data, format="json")
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy(self):
        self.client.force_login(self.user)
        # Send a DELETE request to the destroy endpoint for the first question
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(uuid=self.question_1.uuid).exists())

    def test_admin_can_destroy_for_other_users(self):
        self.client.force_login(self.user_admin)
        # Send a DELETE request to the destroy endpoint for the first question
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(uuid=self.question_1.uuid).exists())

    def test_user_cant_destroy_for_other_users(self):
        self.client.force_login(self.user_1)
        # Send a DELETE request to the destroy endpoint for the first question
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Question.objects.filter(uuid=self.question_1.uuid).exists())

    def test_destroy_anon(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Question.objects.filter(uuid=self.question_1.uuid).exists())


class ChoiceViewSetTests(APITestCase):
    def setUp(self):
        # Create User objects
        self.user = UserFactory()
        self.user_1 = UserFactory()
        self.user_admin = SuperUserFactory()
        # Create a client to make API requests
        self.client = APIClient()
        # Create a Question and Choices mock data
        self.question = QuestionFactory(
            user=self.user, title="What is the meaning of life?"
        )
        self.question_1 = QuestionFactory(user=self.user_1, title="What is Python?")
        self.question_by_admin = QuestionFactory(user=self.user_admin)
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
        # urls
        self.list_url = reverse("api:choice-list")
        self.detail_url = reverse(
            "api:choice-detail", kwargs={"uuid": self.choices[0].uuid}
        )
        # data
        self.choice_data = {
            "question": str(self.question.uuid),
            "text": "A framework",
            "is_correct": False,
        }

    def test_list(self):
        self.client.force_login(self.user_admin)
        # Make a GET request to the endpoint
        response = self.client.get(self.list_url)
        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_user(self):
        self.client.force_login(self.user)
        # Make a GET request to the endpoint
        response = self.client.get(self.list_url)
        # Test response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_anon(self):
        response = self.client.get(self.list_url)
        # Test response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        self.client.force_login(self.user)
        # Make a POST request to the endpoint
        response = self.client.post(self.list_url, self.choice_data, format="json")
        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], self.choice_data["text"])
        self.assertEqual(response.data["is_correct"], self.choice_data["is_correct"])

    def test_create_anon(self):
        response = self.client.post(self.list_url, self.choice_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_for_other_users(self):
        self.client.force_login(self.user_admin)
        # Make a POST request to the endpoint
        response = self.client.post(self.list_url, self.choice_data, format="json")
        choices = Choice.objects.filter(question__uuid=self.question.uuid).count()
        # Test response and if question choices were updated
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(choices, 4)

    def test_user_cant_create_for_other_users(self):
        """Test prevention of {self.user_1} from modifying resources of {self.user}"""
        self.client.force_login(self.user_1)
        # Make a POST request to the endpoint
        response = self.client.post(self.list_url, self.choice_data, format="json")
        choices = Choice.objects.filter(question__uuid=self.question.uuid).count()
        # Test response and if question choices were updated
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(choices, 3)

    def test_retrieve(self):
        self.client.force_login(self.user)
        # Make a GET request to the endpoint
        response = self.client.get(self.detail_url)
        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list(response.data.keys()),
            ["url", "uuid", "question", "question_url", "text", "is_correct"],
        )
        self.assertEqual(response.data["uuid"], str(self.choices[0].uuid))

    def test_retrieve_anon(self):
        response = self.client.get(self.detail_url)
        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.force_login(self.user)
        # Update an existing choice
        response = self.client.put(self.detail_url, self.choice_data, format="json")
        # Test response and data change
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], self.choice_data["text"])
        self.assertTrue(Choice.objects.filter(text=self.choice_data["text"]).exists())

    def test_update_anon(self):
        response = self.client.put(self.detail_url, self.choice_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_for_other_users(self):
        self.client.force_login(self.user_admin)
        # Update an existing choice
        response = self.client.put(self.detail_url, self.choice_data, format="json")
        # Test response and data change
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], self.choice_data["text"])
        self.assertTrue(Choice.objects.filter(text=self.choice_data["text"]).exists())

    def test_user_cant_update_for_other_users(self):
        self.client.force_login(self.user_1)
        # Update an existing choice
        response = self.client.put(self.detail_url, self.choice_data, format="json")
        # Test response and data change
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy(self):
        self.client.force_login(self.user)
        # Send a DELETE request to the destroy endpoint for the first question
        response = self.client.delete(self.detail_url)
        # Test response and data change
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Choice.objects.filter(uuid=self.choices[0].uuid).exists())

    def test_admin_can_destroy_for_other_users(self):
        self.client.force_login(self.user_admin)
        # Send a DELETE request to the destroy endpoint for the first question
        response = self.client.delete(self.detail_url)
        # Test response and data change
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Choice.objects.filter(uuid=self.choices[0].uuid).exists())

    def test_user_cant_destroy_for_other_users(self):
        self.client.force_login(self.user_1)
        # Send a DELETE request to the destroy endpoint for the first question
        response = self.client.delete(self.detail_url)
        # Test response and data change
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_anon(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AnswerViewSetTests(APITestCase):
    def setUp(self):
        # Create a users to use for authentication
        self.user = UserFactory()
        self.user_1 = UserFactory()
        self.user_admin = SuperUserFactory()
        # Create Answers
        self.answers_user = AnswerFactory.create_batch(2, user=self.user)
        self.answers_user_1 = AnswerFactory.create_batch(3, user=self.user_1)
        # Urls
        self.list_url = reverse("api:answer-list")
        self.detail_url_user = reverse(
            "api:answer-detail", kwargs={"uuid": self.answers_user[0].uuid}
        )
        self.detail_url_user_1 = reverse(
            "api:answer-detail", kwargs={"uuid": self.answers_user_1[0].uuid}
        )

    def test_list(self):
        # Test correct list of answers for request.user
        users = [
            {"instance": self.user, "answers_len": 2},
            {"instance": self.user_1, "answers_len": 3},
            {"instance": self.user_admin, "answers_len": 0},
        ]
        for user in users:
            self.client.force_login(user["instance"])
            # Send a GET request to the list endpoint
            response = self.client.get(self.list_url)
            # Test response
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), user["answers_len"])

    def test_list_anon(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_pagination(self):
        self.client.force_login(self.user)
        # Get API response
        response = self.client.get(self.list_url)
        response_keys = list(response.data.keys())
        keys = ["limit", "offset", "count", "next", "previous", "results"]
        # Test response
        self.assertEqual(response_keys, keys)

    def test_retrieve(self):
        self.client.force_login(self.user)
        # Get API response
        response = self.client.get(self.detail_url_user)
        response_keys = list(response.data.keys())
        keys = ["url", "uuid", "question", "choices", "is_correct", "created_at"]
        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_keys, keys)

    def test_retrieve_from_foreign_user(self):
        self.client.force_login(self.user_1)
        # Get API response from self.user
        response = self.client.get(self.detail_url_user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_anon(self):
        response = self.client.get(self.detail_url_user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_create(self):
    #     self.client.login(**self.user_log_pass)
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
