FROM python:3.11

# set the PYTHONUNBUFFERED environment variable to ensure unbuffered output
ENV PYTHONUNBUFFERED=1

# assign a working directory
WORKDIR /app

# update the system and install necessary tools
RUN apt-get update -y && apt-get install netcat-traditional -y
RUN apt-get upgrade -y && apt-get install postgresql gcc python3-dev musl-dev -y

# upgrade pip and install dependencies from requirements.txt
RUN pip install --upgrade pip
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

# copy the project to the working directory
COPY .  /app

# create/run migrations and start the application
ENTRYPOINT sh -c /app/start.sh
