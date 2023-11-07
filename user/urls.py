from django.urls import path

from quiz.views import QuizViewSet

from .views import RequestToCompanyViewSet, UserViewSet

urlpatterns = [
    path('', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path(
        '<int:pk>/',
        UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='user-detail',
    ),

    path('<int:pk>/requests/', UserViewSet.as_view({'get': 'requests'}), name='user-requests'),
    path('<int:pk>/invitations/', UserViewSet.as_view({'get': 'invitations'}), name='user-invitations'),
    path('<int:pk>/members/', UserViewSet.as_view({'get': 'member_companies'}), name='user-company-member'),
    path('<int:pk>/admins/', UserViewSet.as_view({'get': 'admin_companies'}), name='user-company-admin'),

    path(
        '<int:user_pk>/requests/<int:pk>/',
        RequestToCompanyViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'post': 'create'}),
        name='user-request-detail',
    ),
    path(
        '<int:user_pk>/requests/<int:pk>/cancell/',
        RequestToCompanyViewSet.as_view({'post': 'cancell'}),
        name='user-request-cancell',
    ),

    path('<int:pk>/quizzes/', QuizViewSet.as_view({'get': 'user_quizzes'}), name='user-quizzes'),
    path(
        '<int:pk>/quizzes/results/',
        QuizViewSet.as_view({'get': 'user_all_quiz_results'}),
        name='user-quiz-all-results-list',
    ),
]
