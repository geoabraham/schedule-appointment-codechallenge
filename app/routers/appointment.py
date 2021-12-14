from typing import List

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.params import Depends
from pydantic.types import UUID4
from sqlalchemy.orm.session import Session

from .. import models, schemas, schemas_validators
from ..database import get_db
from .user import find_user_appointments

router = APIRouter(prefix="/appointments")


@router.get("/", response_model=List[schemas.Appointment])
async def get_all_appointments(db: Session = Depends(get_db)):
    all_appointments = db.query(models.Appointment).all()
    return all_appointments


@router.get("/{id}", response_model=schemas.Appointment)
async def get_appointment_by_id(id: UUID4, db: Session = Depends(get_db)):
    appt = (
        db.query(models.Appointment)
        .filter(models.Appointment.appointment_id == id)
        .first()
    )

    if not appt:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointment with id: {id} does not exist",
        )

    return appt


@router.get("/users/{user_id}", response_model=List[schemas.Appointment])
async def get_appointments_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user_appointments = find_user_appointments(user_id, db)
    if not user_appointments:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Appointments for the user with id: {user_id} were not found",
        )
    return user_appointments


@router.post(
    "/", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED
)
async def create_appointment(
    payload: schemas.AppointmentCreate, db: Session = Depends(get_db)
):
    schemas_validators.validate_appointment(payload, db)

    new_appointment = models.Appointment(**payload.dict())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.put("/{id}", response_model=schemas.Appointment)
async def update_appointment(
    id: UUID4, payload: schemas.AppointmentUpdate, db: Session = Depends(get_db)
):
    schemas_validators.validate_appointment(payload, db)

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
