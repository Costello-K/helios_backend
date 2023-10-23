from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.test_data import (
    INCORRECT_QUIZ_DATA_MIN_ANSWERS,
    INCORRECT_QUIZ_DATA_MIN_QUESTIONS,
    INCORRECT_QUIZ_DATA_MISSING_TRUE,
    QUIZ_DATA,
    UPDATED_QUIZ_DATA,
)
from tests.test_models import (
    CompanyFactory,
    CompanyMemberAdminFactory,
    FalseAnswerFactory,
    QuestionFactory,
    QuizFactory,
    TrueAnswerFactory,
    UserFactory,
)

from .models import Quiz

User = get_user_model()


class QuizTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_1 = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()
        self.user_4 = UserFactory()

        self.company_1 = CompanyFactory(owner=self.user_1)
        self.company_2 = CompanyFactory(owner=self.user_2)

        self.admin_company_3_1 = CompanyMemberAdminFactory(member=self.user_3, company=self.company_1)

        self.quiz_1 = QuizFactory(company=self.company_1)
        self.quiz_2 = QuizFactory(company=self.company_2)
        self.quiz_3 = QuizFactory(company=self.company_1)

        self.question_1_1 = QuestionFactory(quiz=self.quiz_1)
        self.question_1_2 = QuestionFactory(quiz=self.quiz_1)
        self.question_1_3 = QuestionFactory(quiz=self.quiz_1)
        self.question_2_1 = QuestionFactory(quiz=self.quiz_2)
        self.question_2_2 = QuestionFactory(quiz=self.quiz_2)
        self.question_3_1 = QuestionFactory(quiz=self.quiz_3)
        self.question_3_2 = QuestionFactory(quiz=self.quiz_3)

        self.answer_1 = TrueAnswerFactory(question=(self.question_1_1, self.question_1_2, self.question_1_3,
                                                    self.question_2_1, self.question_2_2, self.question_3_1,
                                                    self.question_3_2))
        self.answer_2 = FalseAnswerFactory(question=(self.question_1_1, self.question_1_2, self.question_1_3,
                                                     self.question_2_1, self.question_2_2, self.question_3_1,
                                                     self.question_3_2))
        self.answer_3 = FalseAnswerFactory(question=(self.question_1_1, self.question_1_3, self.question_2_1,
                                                     self.question_2_2, self.question_3_1))

        self.url_get_quiz_list = reverse('quiz-list', args=[self.company_1.id])
        self.url_get_quiz_1 = reverse('quiz-detail', args=[self.company_1.id, self.quiz_1.id])
        self.url_get_quiz_2 = reverse('quiz-detail', args=[self.company_2.id, self.quiz_2.id])
        self.url_get_quiz_3 = reverse('quiz-detail', args=[self.company_1.id, self.quiz_3.id])

        self.create_quiz_data = QUIZ_DATA
        self.incorrect_quiz_data_1 = INCORRECT_QUIZ_DATA_MIN_QUESTIONS
        self.incorrect_quiz_data_2 = INCORRECT_QUIZ_DATA_MIN_ANSWERS
        self.incorrect_quiz_data_3 = INCORRECT_QUIZ_DATA_MISSING_TRUE
        self.updated_quiz_data = UPDATED_QUIZ_DATA

    def test_quiz_list_non_owner(self):
        self.client.force_authenticate(user=self.user_4)

        response = self.client.get(self.url_get_quiz_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        expected_quizzes = [self.quiz_1.id, self.quiz_3.id]
        quizzes_from_response = [quiz['id'] for quiz in response.data['results']]
        self.assertEqual(sorted(quizzes_from_response), sorted(expected_quizzes))
        self.assertNotIsInstance(response.data['results'][0]['questions'][0]['answers'][0]['is_right'], bool)

    def test_quiz_list_company_owner(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.get(self.url_get_quiz_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        expected_quizzes = [self.quiz_1.id, self.quiz_3.id]
        quizzes_from_response = [quiz['id'] for quiz in response.data['results']]
        self.assertEqual(sorted(quizzes_from_response), sorted(expected_quizzes))
        self.assertIsInstance(response.data['results'][0]['questions'][0]['answers'][0]['is_right'], bool)

    def test_quiz_list_company_admin(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.get(self.url_get_quiz_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        expected_quizzes = [self.quiz_1.id, self.quiz_3.id]
        quizzes_from_response = [quiz['id'] for quiz in response.data['results']]
        self.assertEqual(sorted(quizzes_from_response), sorted(expected_quizzes))
        self.assertIsInstance(response.data['results'][0]['questions'][0]['answers'][0]['is_right'], bool)

    def test_create_quiz_company_owner(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(self.url_get_quiz_list, self.create_quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 4)

    def test_create_quiz_company_admin(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(self.url_get_quiz_list, self.create_quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 4)

    def test_create_quiz_non_owner(self):
        self.client.force_authenticate(user=self.user_4)

        response = self.client.post(self.url_get_quiz_list, self.create_quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Quiz.objects.count(), 3)

    def test_create_quiz_not_valid_min_questions(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(self.url_get_quiz_list, self.incorrect_quiz_data_1, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Quiz.objects.count(), 3)

    def test_create_quiz_not_valid_min_answers(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(self.url_get_quiz_list, self.incorrect_quiz_data_2, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Quiz.objects.count(), 3)

    def test_create_quiz_not_valid_missing_true(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(self.url_get_quiz_list, self.incorrect_quiz_data_3, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Quiz.objects.count(), 3)

    def test_update_quiz_company_owner(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.patch(self.url_get_quiz_3, self.updated_quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_quiz = Quiz.objects.get(id=self.quiz_3.id)
        self.assertEqual(updated_quiz.title, self.updated_quiz_data['title'])
        self.assertEqual(updated_quiz.questions.count(), len(self.updated_quiz_data['questions']))
        self.assertEqual(
            updated_quiz.questions.first().answers.first().text,
            self.updated_quiz_data['questions'][0]['answers'][0]['text']
        )

    def test_update_quiz_company_admin(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.patch(self.url_get_quiz_3, self.updated_quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_quiz = Quiz.objects.get(id=self.quiz_3.id)
        self.assertEqual(updated_quiz.title, self.updated_quiz_data['title'])
        self.assertEqual(updated_quiz.questions.count(), len(self.updated_quiz_data['questions']))
        self.assertEqual(
            updated_quiz.questions.first().answers.first().text,
            self.updated_quiz_data['questions'][0]['answers'][0]['text']
        )

    def test_update_quiz_non_owner(self):
        self.client.force_authenticate(user=self.user_4)

        response = self.client.patch(self.url_get_quiz_3, self.updated_quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        updated_quiz = Quiz.objects.get(id=self.quiz_3.id)
        self.assertNotEqual(updated_quiz.title, self.updated_quiz_data['title'])
        self.assertNotEqual(updated_quiz.questions.count(), len(self.updated_quiz_data['questions']))

    def test_delete_quiz_company_owner(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.delete(self.url_get_quiz_3)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Quiz.objects.count(), 2)

    def test_delete_quiz_company_admin(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.delete(self.url_get_quiz_3)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Quiz.objects.count(), 2)

    def test_delete_quiz_non_owner(self):
        self.client.force_authenticate(user=self.user_4)

        response = self.client.delete(self.url_get_quiz_3)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Quiz.objects.count(), 3)
