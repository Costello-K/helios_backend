from django.utils import timezone

from common.enums import QuizProgressStatus
from quiz.models import Quiz, UserQuizResult


def get_available_user_quiz_list(user_id):
    """
    Method for obtaining a list of quizzes available to the user,
    excluding quizzes that do not have a time limit.
        :param user_id: The ID of the user
        :return: A list of available quizzes for the user
    """
    available_quizzes = []

    quizzes = Quiz.objects.filter(company__companymember__member_id=user_id, frequency__isnull=False)
    for quiz in quizzes:
        last_completed_user_quiz_result = UserQuizResult.objects.filter(
            participant_id=user_id, quiz=quiz, progress_status=QuizProgressStatus.COMPLETED.value
        ).order_by('-updated_at').last()

        if last_completed_user_quiz_result:
            time_since_last_completion = timezone.now() - last_completed_user_quiz_result.updated_at
            delta_time = timezone.timedelta(days=quiz.frequency) - time_since_last_completion
            if delta_time > timezone.timedelta(0):
                continue
        available_quizzes.append(quiz)

    return available_quizzes
