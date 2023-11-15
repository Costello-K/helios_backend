#!/bin/sh

# apply database migrations without interactive prompts
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# compile Django translation messages
python manage.py compilemessages

# collect static files from individual apps into a single location
python manage.py collectstatic --no-input

gunicorn internship_meduzzen_backend.wsgi:application --bind 0.0.0.0:8000
