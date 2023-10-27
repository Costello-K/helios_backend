from django.urls import include, path

urlpatterns = [
    path('users/', include('user.urls')),
    path('companies/', include('company.urls')),
    path('', include('quiz.urls')),
    path('messages/', include('message.urls')),
]
