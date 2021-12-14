from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm.session import Session

from app import models, hashing
from app.schemas import UserLogin
from ..database import get_db

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("/")
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Get user by email
    user = db.query(models.User).filter(models.User.email == payload.email).first()

    # verify matching passwords
    if not user or not hashing.verify_bcrypt_hash(
        payload.user_passwd, user.user_passwd
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid credentials")

    # Create token
    # return token

    return {"token": "bearer token"}
