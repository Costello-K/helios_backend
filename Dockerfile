FROM python:3.11

# set the PYTHONUNBUFFERED environment variable to ensure unbuffered output
ENV PYTHONUNBUFFERED=1

# create directory for the user
RUN mkdir -p /home/ubuntu

# create the user in group
ARG user=ubuntu
ARG group=ubuntu
ARG uid=1001
ARG gid=1001
RUN groupadd -g ${gid} ${group} && useradd -u ${uid} -g ${group} -s /bin/sh ${user}

# create the directories
ENV HOME=/home/ubuntu
ENV APP_HOME=$HOME/backend
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/static
RUN mkdir -p $APP_HOME/logs

# assign a working directory
WORKDIR $APP_HOME

# upgrade pip and install dependencies from requirements.txt
RUN apt-get update && apt-get -y install gettext
RUN pip install --upgrade pip
COPY ./requirements.txt $APP_HOME/
RUN pip install -r requirements.txt

# copy the project to the working directory
COPY .  $APP_HOME

# expose port 8000 for running the application
EXPOSE 8000

# make the start.sh script executable
RUN chmod +x $APP_HOME/start.sh
