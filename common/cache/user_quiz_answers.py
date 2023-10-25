from django.conf import settings
from django.core.cache import cache


def get_user_answers(quiz, user_responses):
    """
    Extract and structure user answers for a quiz.
    Args:
        quiz (Quiz): The quiz for which to extract user answers.
        user_responses (dict): User responses to quiz questions.
    Returns:
        list: List of tuples containing question ID, question text, and user answers.
    """
    user_answers_data = []

    for quiz_question, user_question in zip(quiz.questions.all(), user_responses.get('questions'), strict=True):
        question = {}

        for quiz_answer, user_answer in zip(quiz_question.answers.all(), user_question.get('answers'), strict=True):
            answer = user_answer.get('is_right')

            if answer:
                question[quiz_answer.text] = quiz_answer.is_right == answer

        user_answers_data.append((quiz_question.id, f'{quiz_question.id}_{quiz_question.question_text}', question))

    return user_answers_data


def cache_user_quiz_response(user_quiz_result, user_responses):
    """
    Cache user quiz responses in Redis for later retrieval.
    Args:
        user_quiz_result (UserQuizResult): User's quiz result to associate the responses with.
        user_responses (dict): User responses to a quiz.
    Returns:
        None
    """
    answers_data = get_user_answers(user_quiz_result.quiz, user_responses)
    data_to_store = {}

    for question_id, question, answers in answers_data:
        redis_key = f'user_quiz_result_{user_quiz_result.id}_{question_id}'

        data_to_store[redis_key] = {
            'participant_id': user_quiz_result.participant.id,
            'company_id': user_quiz_result.company.id,
            'quiz_id': user_quiz_result.quiz.id,
            'question': question,
            'answers': answers,
        }

    cache.set_many(data_to_store, settings.REDIS_DATA_EXPIRATION)
