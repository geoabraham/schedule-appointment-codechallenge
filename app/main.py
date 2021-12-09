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
    all_appointments = cursor.fetchall()
    return {"data": all_appointments}


@app.get("/appointments/{user_id}")
async def get_appointment_by_user_id(user_id: int, response: Response):
    user_appointments = find_user_appointments(user_id)
    if len(user_appointments) == 0:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointments for the user with id: {user_id} were not found",
        )
    return {"data": user_appointments}


@app.post("/appointments", status_code=status.HTTP_201_CREATED)
async def create_appointment(payload: Appointment):
    validate_appointment(payload)

    cursor.execute(
        """INSERT INTO public.appointment(
               appointment_date, user_id)
               VALUES ('{0}', {1})
           RETURNING *;""".format(
            payload.appointment_date, payload.user_id
        ),
    )

    new_appointment = cursor.fetchone()
    conn.commit()

    return {"data": new_appointment}


def find_user_appointments(user_id: int):
    cursor.execute(
        """SELECT appointment_date, user_id 
	         FROM public.appointment
            WHERE user_id = {0};""".format(
            user_id
        ),
    )

    user_appointments = cursor.fetchall()

    return user_appointments


def validate_appointment(appt: Appointment):

    if not is_valid_appointment_datetime_format(appt.appointment_date):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Appointment datetime must be in 'YYYY-MM-DD HH:MM' format.",
        )
        
    if not is_valid_future_datetime(appt.appointment_date):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "All appointments must start on a future date.",
        )

    if not is_valid_appointment_start_time(appt.appointment_date):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "All appointments must start and end on the hour or half hour.",
        )

    if not is_valid_appointment_date_for_user(appt.appointment_date, appt.user_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "A user can only have 1 appointment on a calendar date.",
        )


def is_valid_appointment_datetime_format(appt_date):
    try:
        datetime.strptime(str(appt_date), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    return True


def is_valid_appointment_date_for_user(appointment_date, user_id):
    cursor.execute(
        """SELECT appointment_date, user_id 
	         FROM public.appointment
            WHERE user_id = {0}
              AND appointment_date = '{1}';""".format(
            user_id, appointment_date
        ),
    )

    user_appointments = cursor.fetchall()
    return len(user_appointments) == 0


def is_valid_appointment_start_time(appt_date):
    if appt_date.minute % 30 != 0:
        return False
    return True


def is_valid_future_datetime(appt_date):
    if appt_date < datetime.now():
        return False
    return True
