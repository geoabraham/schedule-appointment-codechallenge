from datetime import datetime

from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status
from . import schemas, models


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
