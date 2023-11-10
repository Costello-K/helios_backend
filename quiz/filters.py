from django_filters import rest_framework as filters

from quiz.models import UserQuizResult


class UserQuizResultFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name='participant_id')

    class Meta:
        model = UserQuizResult
        fields = {
            'participant_id': ['exact'],
            'progress_status': ['exact'],
            'company_id': ['exact'],
            'quiz_id': ['exact'],
        }
