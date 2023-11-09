import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internship_meduzzen_backend.settings')

app = Celery('internship_meduzzen_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
