# Pull image from Docker Hub
FROM python:3.8-slim-buster
MAINTAINER RicardoAVS

# Set enviroment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a directory in our Dock app
RUN mkdir /app

# Creating a working directory for the django project
WORKDIR /app

# Copy requirments to the container
COPY Pipfile Pipfile.lock /app/

# Install the requirements to the container
# --system: Install all packages into the system python and not into virtualenv
# --deploy: So build fails if Pipefile is out of date
# --ignore-pipefile: avoid messing up out set up
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

# For security reasons we create a user to run all proccesses for our project
RUN adduser --disabled-password user
USER user

# Copy the project files into the working directory
COPY . /app/

# Open port on the container
EXPOSE 8000
