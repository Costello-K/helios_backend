Project name:
Backend internship at "Meduzzen" company

Project description:

This project is an API application. Users can create companies, manage their employees, and create assessment tests for their employees. In addition, the system provides a function to notify employees about new tests. The project is built using the Django REST Framework (DRF) for the API.

Development Tools:

    Python >= 3.11
    
    Django == 4.2.5
    Django REST Framework 3.14.0


Installation and running the project:

1) Clone the repository

       https://github.com/Costello90/internship_meduzzen_backend.git
2) Create a virtual environment

       cd internship_meduzzen_backend
       python -m venv venv

3) Activate virtual environment

   Linux

       source venv/bin/activate

   Windows

       ./venv/Scripts/activate
4) Install dependencies:

       pip install -r requirements.txt
5) In the root directory of the project, create an ".env" file. In the ".env" file, copy all the variables from the ".env.sample" file and give them values
6) Run tests

       python manage.py test
7) Run server

       python manage.py runserver
8) Links

    DRF API 

        http://127.0.0.1:8000/




License:

Copyright (c) 2023-present, Kostiantyn Kondratenko
