from datetime import datetime

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

app = FastAPI()


class Appointment(BaseModel):
    appointment_date: datetime
    user_id: int


appointments = [{"appointment_date": datetime.now(), "user_id": 0}]


@app.get('/')
async def root():
    return {'message': 'Hello World!!'}


@app.get('/appointments')
async def get_all_appointments():
    return {"data": appointments}


@app.get('/appointments/{user_id}')
async def get_appointment_by_user_id(user_id: int, response: Response):
    result = find_user_appointments(user_id)
    if len(result) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
    return {"data": result}


@app.post('/appointments')
async def create_appointment(payload: Appointment, response: Response):
    try:
        datetime.strptime(str(payload.appointment_date), "%Y-%m-%d %H:%M:%S")
    except ValueError as ve:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Appointment datetime must be in 'YYYY-MM-DD HH:MM' format."}

    if payload.appointment_date.minute % 30 != 0 or payload.appointment_date.second != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "All appointments must start and end on the hour or half hour."}

    if not is_valid_appointment_date(payload.appointment_date, payload.user_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "a user can only have 1 appointment on a calendar date"}

    appointments.append(payload.dict())
    response.status_code = status.HTTP_201_CREATED
    return {"data": payload}


def find_user_appointments(user_id):
    return [a for a in appointments if a["user_id"] == user_id]


def is_valid_appointment_date(appointment_date, user_id):
    result = [a for a in appointments if
              a["appointment_date"].date() == appointment_date.date() and a["user_id"] == user_id]
    return len(result) == 0
