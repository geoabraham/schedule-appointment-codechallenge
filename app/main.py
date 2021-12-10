import time
from datetime import datetime

import psycopg2
from fastapi import FastAPI, HTTPException, status
from fastapi.params import Depends
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

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


@app.get("/")
async def root():
    return {"message": "Hello World!!"}


@app.get("/appointments")
async def get_all_appointments(db: Session = Depends(get_db)):
    all_appointments = db.query(models.Appointment).all()
    return {"data": all_appointments}


@app.get("/appointments/{user_id}")
async def get_appointment_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user_appointments = find_user_appointments(user_id, db)
    if not user_appointments:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointments for the user with id: {user_id} were not found",
        )
    return {"data": user_appointments}


@app.post("/appointments", status_code=status.HTTP_201_CREATED)
async def create_appointment(payload: Appointment, db: Session = Depends(get_db)):

    validate_appointment(payload, db)

    new_appointment = models.Appointment(**payload.dict())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return {"data": new_appointment}


def find_user_appointments(user_id: int, db: Session):
    user_appointments = (
        db.query(models.Appointment).filter(models.Appointment.user_id == user_id).all()
    )
    return user_appointments


def validate_appointment(appt: Appointment, db: Session):

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

    if not is_valid_appointment_date_for_user(appt.appointment_date, appt.user_id, db):
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


def is_valid_appointment_date_for_user(appointment_date, user_id, db: Session):
    user_appointments = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.appointment_date == appointment_date
            and models.Appointment.user_id == user_id
        )
        .first()
    )

    return user_appointments is None


def is_valid_appointment_start_time(appt_date):
    if appt_date.minute % 30 != 0:
        return False
    return True


def is_valid_future_datetime(appt_date):
    if appt_date < datetime.now():
        return False
    return True
