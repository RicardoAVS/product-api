# Pull image from Docker Hub
FROM python:3.8-alpine
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

# Install postgresql client, we don't want to overload Docker img
# with unneccesary files that is why we use the --no-cache flag
RUN apk add --update --no-cache postgresql-client

# Installing temporary packages that need to be installed while 
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev

RUN pip3 install -r /requirements.txt

# Delete temporary requirements
RUN apk del .tmp-build-deps

# For security reasons we create a user to run all proccesses for our project
RUN adduser --disabled-password user
USER user

# Copy the project files into the working directory
COPY ./app /app 

# Open port on the container
EXPOSE 8000
