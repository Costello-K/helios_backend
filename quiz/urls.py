from django.urls import path

from .views import QuizViewSet

urlpatterns = [
    path(
        'companies/<int:company_pk>/quizzes/',
        QuizViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='quiz-list'
    ),
    path(
        'companies/<int:company_pk>/quizzes/<int:pk>/',
        QuizViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='quiz-detail',
    ),
    path(
        'companies/<int:company_pk>/quizzes/<int:pk>/start/',
        QuizViewSet.as_view({'post': 'quiz_start'}),
        name='quiz-start'
    ),
    path(
        'companies/<int:company_pk>/quizzes/<int:pk>/complete/',
        QuizViewSet.as_view({'post': 'quiz_complete'}),
        name='quiz-complete'
    ),
    path(
        'companies/<int:company_pk>/quizzes/results/',
        QuizViewSet.as_view({'get': 'company_quiz_results'}),
        name='company-quiz-results-list'
    ),
    path(
        'companies/<int:company_pk>/quizzes/results/<int:member_pk>/',
        QuizViewSet.as_view({'get': 'company_member_quiz_results'}),
        name='company-member-quiz-results-list'
    ),
    path(
        'companies/<int:company_pk>/quizzes/<int:pk>/results/',
        QuizViewSet.as_view({'get': 'user_quiz_results'}),
        name='user-quiz-results-list'
    ),
    path('analytics/quizzes/', QuizViewSet.as_view({'get': 'quizzes_analytics'}), name='quiz-analytics-list'),
    path('analytics/users/', QuizViewSet.as_view({'get': 'users_analytics'}), name='user-analytics-list'),
    path('analytics/users/<int:pk>/', QuizViewSet.as_view({'get': 'user_analytics'}), name='user-analytics-detail'),
    path(
        'analytics/companies/<int:pk>/',
        QuizViewSet.as_view({'get': 'company_analytics'}),
        name='company-analytics-detail',
    ),
]
