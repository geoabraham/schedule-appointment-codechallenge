from datetime import datetime
from time import sleep
from typing import List

import psycopg2
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Depends
from psycopg2.extras import RealDictCursor
from pydantic.types import UUID4
from sqlalchemy.orm.session import Session

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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
        sleep(30)


@app.get("/")
async def root():
    return {"message": "Hello World!!"}


@app.get("/appointments", response_model=List[schemas.Appointment])
async def get_all_appointments(db: Session = Depends(get_db)):
    all_appointments = db.query(models.Appointment).all()
    return all_appointments


@app.get("/appointments/{id}", response_model=schemas.Appointment)
async def get_appointment_by_id(id: UUID4, db: Session = Depends(get_db)):
    appt = (
        db.query(models.Appointment)
        .filter(models.Appointment.appointment_id == id)
        .first()
    )
    return appt


@app.get("/appointments/{user_id}", response_model=List[schemas.Appointment])
async def get_appointments_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user_appointments = find_user_appointments(user_id, db)
    if not user_appointments:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointments for the user with id: {user_id} were not found",
        )
    return user_appointments


@app.post(
    "/appointments",
    response_model=schemas.Appointment,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    payload: schemas.CreateAppointment, db: Session = Depends(get_db)
):
    validate_appointment(payload, db)

    new_appointment = models.Appointment(**payload.dict())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@app.delete("/appointments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(id: UUID4, db: Session = Depends(get_db)):
    appt_query = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == id
    )

    if not appt_query.first():
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointment with id: {id} does not exist",
        )

    appt_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/appointments/{id}", response_model=schemas.Appointment)
async def update_appointment(
    id: UUID4, payload: schemas.UpdateAppointment, db: Session = Depends(get_db)
):
    appt_query = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == id
    )

    if not appt_query.first():
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointment with id: {id} does not exist",
        )

    appt_query.update(payload.dict(), synchronize_session=False)
    db.commit()

    return appt_query.first()


def find_user_appointments(user_id: int, db: Session):
    user_appointments = (
        db.query(models.Appointment).filter(models.Appointment.user_id == user_id).all()
    )
    return user_appointments


def validate_appointment(appt: schemas.Appointment, db: Session):

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
            models.Appointment.appointment_date == appointment_date,
            models.Appointment.user_id == user_id,
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
