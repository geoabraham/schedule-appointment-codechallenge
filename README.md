# Appointment Scheduler

This repository contains a basic Appointment Scheduler in FastAPI.

## Setup

For starting the developer environment:

    make init

Do not forget to activate your new virtual environment

    source venv/bin/activate

To run the FastAPI application in debug use:

    make service-run

## Configuration Setup

Create a `.env` file in the root directory of your project.
Add environment-specific variables on new lines in the form of `NAME=VALUE` .
These are the variables used in the application.
Complete with the values relative to your development environment.

    DB_HOSTNAME=localhost
    DB_PORT=5432
    DB_PASSWORD=Súper-Secret-And-Unique-P4ssword!
    DB_NAME=appointment-scheduler
    DB_USERNAME=dbusername
    SECRET_KEY=1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik9ol0pñ
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60

## OpenAPI

    http://127.0.0.1:8000/docs

## ReDoc

    http://127.0.0.1:8000/redoc

## Server Model

    {
        "appointment_date": "datetime",
        "user_id": "int"
    }
