from django.urls import include, path

urlpatterns = [
    path('users/', include('user.urls')),
    path('users/', include('notification.urls')),
    path('companies/', include('company.urls')),
    path('', include('quiz.urls')),
]
