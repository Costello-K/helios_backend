FROM python:3.11

# set the PYTHONUNBUFFERED environment variable to ensure unbuffered output
ENV PYTHONUNBUFFERED=1

# assign a working directory
WORKDIR /app

# upgrade pip and install dependencies from requirements.txt
RUN pip install --upgrade pip
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

# copy the project to the working directory
COPY .  /app

# expose port 8000 for running the application
EXPOSE 8000

# make the start.sh script executable
RUN chmod +x /app/start.sh

# create/run migrations and start the application
ENTRYPOINT ["/app/start.sh"]
