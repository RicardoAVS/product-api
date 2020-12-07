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
COPY ./requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

# For security reasons we create a user to run all proccesses for our project
RUN adduser --disabled-password user
USER user

# Copy the project files into the working directory
COPY ./app /app 

# Open port on the container
EXPOSE 8000
