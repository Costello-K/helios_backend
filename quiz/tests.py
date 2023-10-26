from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from common.enums import QuizProgressStatus
from tests.test_data import (
    CREATE_QUIZ_DATA,
    CREATE_QUIZ_VS_ANSWER_DATA,
    INCORRECT_QUIZ_DATA_MIN_ANSWERS,
    INCORRECT_QUIZ_DATA_MIN_QUESTIONS,
    INCORRECT_QUIZ_DATA_MISSING_TRUE,
    QUIZ_DATA,
    UPDATED_QUIZ_DATA,
    USER_QUIZ_ANSWERS_DATA,
)
from tests.test_models import (
    CompanyFactory,
    CompanyMemberAdminFactory,
    FalseAnswerFactory,
    QuestionFactory,
    QuizFactory,
    TrueAnswerFactory,
    UserFactory,
    UserQuizResultCompletionFactory,
    UserQuizResultFactory,
)

from .models import Quiz, UserQuizResult

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

        self.result_1_2 = UserQuizResultCompletionFactory(participant=self.user_2, company=self.company_1,
                                                          quiz=self.quiz_1)
        self.result_2_4 = UserQuizResultCompletionFactory(participant=self.user_4, company=self.company_2,
                                                          quiz=self.quiz_2)
        self.result_3_2 = UserQuizResultCompletionFactory(participant=self.user_2, company=self.company_1,
                                                          quiz=self.quiz_3)
        self.result_1_3 = UserQuizResultCompletionFactory(participant=self.user_3, company=self.company_1,
                                                          quiz=self.quiz_1)
        self.result_2_3 = UserQuizResultCompletionFactory(participant=self.user_3, company=self.company_2,
                                                          quiz=self.quiz_2)
        self.result_3_3 = UserQuizResultCompletionFactory(participant=self.user_3, company=self.company_1,
                                                          quiz=self.quiz_3)

        self.quiz_result_not_completion = UserQuizResultFactory(participant=self.user_3, company=self.company_1,
                                                                quiz=self.quiz_3)

        self.url_get_quiz_list = reverse('quiz-list', args=[self.company_1.id])
        self.url_get_quiz_1 = reverse('quiz-detail', args=[self.company_1.id, self.quiz_1.id])
        self.url_get_quiz_2 = reverse('quiz-detail', args=[self.company_2.id, self.quiz_2.id])
        self.url_get_quiz_3 = reverse('quiz-detail', args=[self.company_1.id, self.quiz_3.id])

        self.create_quiz_data = QUIZ_DATA
        self.incorrect_quiz_data_1 = INCORRECT_QUIZ_DATA_MIN_QUESTIONS
        self.incorrect_quiz_data_2 = INCORRECT_QUIZ_DATA_MIN_ANSWERS
        self.incorrect_quiz_data_3 = INCORRECT_QUIZ_DATA_MISSING_TRUE
        self.updated_quiz_data = UPDATED_QUIZ_DATA
        self.create_quiz_data_2 = CREATE_QUIZ_DATA
        self.quiz_complete_data_2 = USER_QUIZ_ANSWERS_DATA
        self.create_quiz_data_3 = CREATE_QUIZ_VS_ANSWER_DATA

    def test_quizzes_analytics_list(self):
        self.client.force_authenticate(user=self.user_3)
        url = reverse('quiz-analytics-list')

        response = self.client.get(url)
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), Quiz.objects.count())
        expected_results = [self.result_3_2.id, self.result_3_3.id]
        results_from_response = [result['quiz_results'] for result in data if result['id'] == self.quiz_3.id]
        results_id = [result['id'] for result in results_from_response[0]]
        self.assertEqual(sorted(results_id), sorted(expected_results))

    def test_users_analytics_list(self):
        self.client.force_authenticate(user=self.user_3)
        url = reverse('user-analytics-list')

        response = self.client.get(url)
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), User.objects.count())
        expected_results = [self.result_1_3.id, self.result_2_3.id, self.result_3_3.id]
        results_from_response = [result['quiz_results'] for result in data if result['id'] == self.user_3.id]
        results_id = [result['id'] for result in results_from_response[0]]
        self.assertEqual(sorted(results_id), sorted(expected_results))

    def test_user_analytics_detail(self):
        self.client.force_authenticate(user=self.user_3)
        url = reverse('user-analytics-detail', args=[self.user_3.id])

        response = self.client.get(url)
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['quiz_results']), UserQuizResult.objects.filter(
                             participant_id=self.user_3.id, progress_status=QuizProgressStatus.COMPLETED.value).count())
        expected_results = [self.result_1_3.id, self.result_2_3.id, self.result_3_3.id]
        results_from_response = [result['id'] for result in data['quiz_results']]
        self.assertEqual(sorted(results_from_response), sorted(expected_results))

    def test_quiz_list_non_owner(self):
        self.client.force_authenticate(user=self.user_4)

        response = self.client.get(self.url_get_quiz_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        expected_quizzes = [self.quiz_1.id, self.quiz_3.id]
        quizzes_from_response = [quiz['id'] for quiz in response.data['results']]
        self.assertEqual(sorted(quizzes_from_response), sorted(expected_quizzes))

    def test_quiz_list_company_owner(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.get(self.url_get_quiz_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        expected_quizzes = [self.quiz_1.id, self.quiz_3.id]
        quizzes_from_response = [quiz['id'] for quiz in response.data['results']]
        self.assertEqual(sorted(quizzes_from_response), sorted(expected_quizzes))

    def test_quiz_list_company_admin(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.get(self.url_get_quiz_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        expected_quizzes = [self.quiz_1.id, self.quiz_3.id]
        quizzes_from_response = [quiz['id'] for quiz in response.data['results']]
        self.assertEqual(sorted(quizzes_from_response), sorted(expected_quizzes))

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

    def test_create_complete_quiz_result(self):
        UserQuizResult.objects.all().delete()
        self.client.force_authenticate(user=self.user_1)

        # create quiz #3
        create_response_2 = self.client.post(self.url_get_quiz_list, self.create_quiz_data_2, format='json')
        quiz_id_2 = create_response_2.data['id']
        # create quiz #4
        create_response_3 = self.client.post(self.url_get_quiz_list, self.create_quiz_data_3, format='json')
        quiz_id_3 = create_response_3.data['id']

        # take the quiz to get started
        self.client.force_authenticate(user=self.user_4)
        url_quiz_start = reverse('quiz-start', args=[self.company_1.id, quiz_id_2])

        start_response = self.client.post(url_quiz_start, format='json')

        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserQuizResult.objects.first().progress_status, QuizProgressStatus.STARTED.value)
        self.assertNotIsInstance(start_response.data['questions'][0]['answers'][0]['is_right'], bool)

        # let's try to re-create duplicate UserQuizResult
        self.client.post(url_quiz_start, format='json')
        self.assertEqual(UserQuizResult.objects.count(), 1)

        # send the quiz for check
        url_quiz_complete = reverse('quiz-complete', args=[self.company_1.id, quiz_id_2])

        complete_response = self.client.post(url_quiz_complete, self.quiz_complete_data_2, format='json')
        data = complete_response.data

        self.assertEqual(data['correct_answers'], 5/7 + 0.5 + 1)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['progress_status'], QuizProgressStatus.COMPLETED.value)
        self.assertEqual(Decimal(data['user_rating']), Decimal(100 * (5/7 + 0.5 + 1)/3).quantize(Decimal('1.00')))
        self.assertEqual(Decimal(data['company_average_score']),
                         Decimal(100 * (5/7 + 0.5 + 1)/3).quantize(Decimal('1.00')))
        self.assertEqual(data['participant']['id'], self.user_4.id)
        self.assertEqual(data['company']['id'], self.company_1.id)
        self.assertEqual(data['quiz']['id'], quiz_id_2)

        # let's try to create UserQuizResult with old data
        self.client.post(url_quiz_start, format='json')
        self.assertEqual(UserQuizResult.objects.count(), 2)

        # let's try to create UserQuizResult with new data
        url_quiz_start_3 = reverse('quiz-start', args=[self.company_1.id, quiz_id_3])
        self.client.post(url_quiz_start_3, format='json')
        self.assertEqual(UserQuizResult.objects.count(), 3)

        # send the new quiz for check
        url_quiz_complete_3 = reverse('quiz-complete', args=[self.company_1.id, quiz_id_3])

        complete_response_3 = self.client.post(url_quiz_complete_3, self.create_quiz_data_3, format='json')
        data_3 = complete_response_3.data

        self.assertEqual(data_3['correct_answers'], 2)
        self.assertEqual(data_3['correct_answers_collector'], 5 / 7 + 0.5 + 1 + 2)
        self.assertEqual(data_3['total_questions'], 2)
        self.assertEqual(data_3['total_questions_collector'], 3 + 2)
        self.assertEqual(Decimal(data_3['user_rating']),
                         Decimal(100 * (5 / 7 + 0.5 + 1 + 2) / (3 + 2)).quantize(Decimal('1.00')))
        self.assertEqual(Decimal(data_3['company_average_score']),
                         Decimal(100 * (5 / 7 + 0.5 + 1 + 2) / (3 + 2)).quantize(Decimal('1.00')))
