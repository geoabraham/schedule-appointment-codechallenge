import time
from datetime import datetime

from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from pydantic.utils import import_string

import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI()


class Appointment(BaseModel):
    appointment_date: datetime
    user_id: int


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="appointment-scheduler",
            user="gabraham",
            password="#pSQL_00!",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        break
    except Exception as error:
        print("Database connection failed")
        print("error: ", error)
        print("Reconnecting in 30 seconds...")
        time.sleep(30)

appointments = [{"appointment_date": datetime.now(), "user_id": 0}]


@app.get("/")
async def root():
    return {"message": "Hello World!!"}


@app.get("/appointments")
async def get_all_appointments():
    cursor.execute(
        """SELECT appointment_date, user_id 
	         FROM public.appointment;"""
    )
    appointments = cursor.fetchall()
    return {"data": appointments}


@app.get("/appointments/{user_id}")
async def get_appointment_by_user_id(user_id: int, response: Response):
    result = find_user_appointments(user_id)
    if len(result) == 0:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointments for the user with id: {user_id} were not found",
        )
    return {"data": result}


@app.post("/appointments", status_code=status.HTTP_201_CREATED)
async def create_appointment(payload: Appointment):
    try:
        datetime.strptime(str(payload.appointment_date), "%Y-%m-%d %H:%M:%S")
    except ValueError as ve:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Appointment datetime must be in 'YYYY-MM-DD HH:MM' format.",
        )

    if (
        payload.appointment_date.minute % 30 != 0
        or payload.appointment_date.second != 0
    ):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "All appointments must start and end on the hour or half hour.",
        )

    if not is_valid_appointment_date(payload.appointment_date, payload.user_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "A user can only have 1 appointment on a calendar date.",
        )

    cursor.execute(
        """INSERT INTO public.appointment(
               appointment_date, user_id)
               VALUES (%s, %s)
           RETURNING *;""",
        (payload.appointment_date, payload.user_id),
    )

    new_appointment = cursor.fetchone()
    conn.commit()

    return {"data": new_appointment}


def find_user_appointments(user_id):
    return [a for a in appointments if a["user_id"] == user_id]


def is_valid_appointment_date(appointment_date, user_id):
    result = [
        a
        for a in appointments
        if a["appointment_date"].date() == appointment_date.date()
        and a["user_id"] == user_id
    ]
    return len(result) == 0
