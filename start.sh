#!/bin/sh

# apply database migrations without interactive prompts
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# start the Django server
python manage.py runserver 0.0.0.0:8000
