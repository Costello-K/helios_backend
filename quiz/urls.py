from django.urls import path

from .views import QuizViewSet

urlpatterns = [
    path('<int:company_pk>/quizzes/', QuizViewSet.as_view({'get': 'list', 'post': 'create'}), name='quiz-list'),
    path(
        '<int:company_pk>/quizzes/<int:pk>/',
        QuizViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='quiz-detail',
    ),
    path('<int:company_pk>/quizzes/<int:pk>/start/', QuizViewSet.as_view({'post': 'quiz_start'}), name='quiz-start'),
    path(
        '<int:company_pk>/quizzes/<int:pk>/complete/',
        QuizViewSet.as_view({'post': 'quiz_complete'}),
        name='quiz-complete'
    ),
    path(
        '<int:company_pk>/quizzes/results/',
        QuizViewSet.as_view({'get': 'company_quiz_results'}),
        name='company-quiz-results-list'
    ),
    path(
        '<int:company_pk>/quizzes/results/<int:member_pk>/',
        QuizViewSet.as_view({'get': 'company_member_quiz_results'}),
        name='company-member-quiz-results-list'
    ),
    path(
        '<int:company_pk>/quizzes/<int:pk>/results/',
        QuizViewSet.as_view({'get': 'user_quiz_results'}),
        name='user-quiz-results-list'
    ),
]
