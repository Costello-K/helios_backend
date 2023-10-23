from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuizViewSet

router = DefaultRouter()
router.register('', QuizViewSet, basename='quiz')

urlpatterns = [
    path('<int:company_pk>/quizzes/', include(router.urls)),
]
