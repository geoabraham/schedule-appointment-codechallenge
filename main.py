from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Appointment(BaseModel):
    appointment_date: datetime
    user_id: int


appointments = [{"appointment_date": datetime.now(), "user_id": 0}]


@app.get('/')
async def root():
    return {'message': 'Hello World!!'}


@app.get('/appointment/')
async def get_all_appointments():
    return {"data": appointments}


@app.get('/appointment/{user_id}')
async def get_appointment_by_user_id(user_id: int):
    return {"data": None}


@app.post('/appointment')
async def create_appointment(payload: Appointment):
    appointments.append(payload.dict())
    return {"data": payload}
