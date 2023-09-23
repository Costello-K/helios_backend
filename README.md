Project name:
Backend internship at "Meduzzen" company

Project description:

This project is an API application. Users can create companies, manage their employees, and create assessment quizzes for their employees. In addition, the system provides a function to notify employees about new quizzes. The project is built using the Django REST Framework (DRF) for the API.

Development Tools:

    Python >= 3.11
    
    Django == 4.2.5
    Django REST Framework 3.14.0

    Docker 20.10.2


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
7) Create migrations

       python manage.py makemigrations
8) Apply migrations to the database

       python manage.py migrate
9) Run server

       python manage.py runserver
10) Links

    DRF API 

        http://127.0.0.1:8000/


Deploying the application using Docker:

1) Ensure that Docker and Docker Compose are installed on your system.

2) In the root directory of the project, create an ".env" file. In the ".env" file, copy all the variables from the ".env.sample" file and give them values

3) Build the Docker images:

       docker-compose build
4) Start the containers:

       docker-compose up
5) You can now open a web browser and see the application in action at the following address.
       
       http://127.0.0.1:8000
6) If you need to run the tests yourself, you need to run the commands:
       
       docker-compose up
       docker container ls
   You need to copy the ID of the running container with our application and paste it instead of "<container_id>"

       docker exec -it <container_id> /bin/bash
       python manage.py test

License:

Copyright (c) 2023-present, Kostiantyn Kondratenko
