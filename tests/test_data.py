QUIZ_DATA = {
    'title': 'Quiz title',
    'questions': [
        {
            'question_text': 'Question 1',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 2', 'is_right': False},
                {'text': 'Answer 2', 'is_right': True},
            ]
        },
        {
            'question_text': 'Question 2',
            'answers': [
                {"text": "Answer 1", "is_right": True},
                {"text": "Answer 2", "is_right": False},
            ]
        },
    ]
}

CREATE_QUIZ_DATA = {
    'title': 'Quiz title',
    'questions': [
        {
            'question_text': 'Question 1',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 2', 'is_right': True},
                {'text': 'Answer 3', 'is_right': False},
                {'text': 'Answer 4', 'is_right': True},
                {'text': 'Answer 5', 'is_right': False},
                {'text': 'Answer 6', 'is_right': True},
                {'text': 'Answer 7', 'is_right': False},
            ]
        },
        {
            'question_text': 'Question 2',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 2', 'is_right': False},
                {'text': 'Answer 3', 'is_right': False},
                {'text': 'Answer 4', 'is_right': False},
            ]
        },
        {
            'question_text': 'Question 3',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 2', 'is_right': True},
                {'text': 'Answer 3', 'is_right': False},
                {'text': 'Answer 4', 'is_right': False},
            ]
        }
    ]
}

USER_QUIZ_ANSWERS_DATA = {
    'questions': [
        {
            'question_text': 'Question 1',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 2', 'is_right': True},
                {'text': 'Answer 3', 'is_right': False},
                {'text': 'Answer 4', 'is_right': False},
                {'text': 'Answer 5', 'is_right': False},
                {'text': 'Answer 6', 'is_right': True},
                {'text': 'Answer 7', 'is_right': False},
            ]
        },
        {
            'question_text': 'Question 2',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 3', 'is_right': False},
                {'text': 'Answer 2', 'is_right': True},
                {'text': 'Answer 4', 'is_right': False},
            ]
        },
        {
            'question_text': 'Question 3',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 2', 'is_right': True},
                {'text': 'Answer 3', 'is_right': False},
                {'text': 'Answer 4', 'is_right': False},
            ]
        }
    ]
}

CREATE_QUIZ_VS_ANSWER_DATA = {
    'title': 'Quiz title',
    'questions': [
        {
            'question_text': 'Question 1',
            'answers': [
                {'text': 'Answer 10', 'is_right': True},
                {'text': 'Answer 11', 'is_right': False},
            ]
        },
        {
            'question_text': 'Question 2',
            'answers': [
                {"text": "Answer 12", "is_right": True},
                {"text": "Answer 13", "is_right": False},
            ]
        },
    ]
}

INCORRECT_QUIZ_DATA_MIN_QUESTIONS = {
    'title': 'Quiz title',
    'questions': [
        {
            'question_text': 'Question 1',
            'answers': [
                {'text': 'Answer 1', 'is_right': True},
                {'text': 'Answer 1', 'is_right': True},
            ]
        }
    ]
}

INCORRECT_QUIZ_DATA_MIN_ANSWERS = {
    'title': 'Quiz title',
    'questions': [
        {
            'question_text': 'Question 1',
            'answers': [{'text': 'Answer 1', 'is_right': True}]
        },
        {
            'question_text': 'Question 1',
            'answers': [{'text': 'Answer 1', 'is_right': True}]
        }
    ]
}

INCORRECT_QUIZ_DATA_MISSING_TRUE = {
    'title': 'Quiz title',
    'questions': [
        {
            'question_text': 'Question 1',
            'answers': [
                {'text': 'Answer 1', 'is_right': False},
                {'text': 'Answer 1', 'is_right': False},
            ]
        },
        {
            'question_text': 'Question 2',
            'answers': [
                {"text": "Answer 1", "is_right": True},
                {"text": "Answer 2", "is_right": False},
            ]
        },
    ]
}

UPDATED_QUIZ_DATA = {
    'title': 'Update quiz title',
    'questions': [
        {
            'question_text': 'New question 1',
            'answers': [
                {'text': 'Answer 3', 'is_right': True},
                {'text': 'Answer 4', 'is_right': False},
            ]
        },
        {
            'question_text': 'New question 2',
            'answers': [
                {"text": "Answer 1", "is_right": True},
                {"text": "Answer 1", "is_right": True},
                {"text": "Answer 2", "is_right": False},
            ]
        },
        {
            'question_text': 'New question 3',
            'answers': [
                {"text": "Answer 5", "is_right": True},
                {"text": "Answer 6", "is_right": False},
                {"text": "Answer 6", "is_right": False},
            ]
        },
    ]
}
