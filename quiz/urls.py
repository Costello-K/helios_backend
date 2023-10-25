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
]
