from app import hashing, models, oauth2, schemas
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from ..database import get_db

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("/", response_model=schemas.Token)
async def login(
    payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(models.User.email == payload.username).first()

    if not user or not hashing.verify_bcrypt_hash(payload.password, user.user_passwd):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid credentials")

    access_token = oauth2.create_access_token({"user_id": user.user_id})

    return {"access_token": access_token, "token_type": "bearer"}
