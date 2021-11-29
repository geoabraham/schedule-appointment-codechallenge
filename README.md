# Appointment Scheduler

This repository contains a basic Appointment Scheduler in FastAPI.

## Setup

For starting the developer environment:

    make init

Do not forget to activate your new virtual environment

    source venv/bin/activate

To run the FastAPI application in debug use:

    make service-run

## OpenAPI

    http://127.0.0.1:8000/docs

## Server Model

```json
{
    "appointment_date": "datetime",
    "user_id": "int"
}
```