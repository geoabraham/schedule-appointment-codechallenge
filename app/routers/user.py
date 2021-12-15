from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from pydantic.types import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from app import oauth2

from .. import hashing, models, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[schemas.User])
async def get_all_users(db: Session = Depends(get_db)):
    all_users = db.query(models.User).all()
    return all_users


@router.get("/{id}", response_model=schemas.User)
async def get_appointment_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == id).first()
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"User with id: {id} does not exist",
        )
    return user


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    hashed_passwd = hashing.hash_bcrypt(payload.user_passwd)
    payload.user_passwd = hashed_passwd

    new_user = models.User(**payload.dict())
    db.add(new_user)

    try:
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        if "duplicate key" in str(ie):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"Key (email)=({payload.email}) already exists",
            )
        else:
            raise ie

    db.refresh(new_user)

    return new_user


def find_user_appointments(user_id: int, db: Session):
    user_appointments = (
        db.query(models.Appointment).filter(models.Appointment.user_id == user_id).all()
    )
    return user_appointments
