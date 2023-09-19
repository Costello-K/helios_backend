from django.urls import path, include

urlpatterns = [
    path('users/', include('user.urls')),
    path('companies/', include('company.urls')),
    path('quizzes/', include('quiz.urls')),
    path('messages/', include('message.urls')),
]
