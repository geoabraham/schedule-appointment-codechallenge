from time import sleep
from typing import List

import psycopg2
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Depends
from psycopg2.extras import RealDictCursor
from pydantic.types import UUID4
from sqlalchemy.orm.session import Session

from . import models, schemas, schemas_validators
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
    schemas_validators.validate_appointment(payload, db)

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
