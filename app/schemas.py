from datetime import datetime
from pydantic.types import UUID4

from pydantic import BaseModel, EmailStr


class BaseAppointment(BaseModel):
    appointment_date: datetime
    user_id: int


class AppointmentCreate(BaseAppointment):
    pass


class AppointmentUpdate(BaseAppointment):
    pass


class Appointment(BaseAppointment):
    appointment_id: UUID4

    class Config:
        orm_mode = True


class BaseUser(BaseModel):
    email: EmailStr
    user_passwd: str


class UserCreate(BaseUser):
    pass


class UserLogin(BaseModel):
    pass


class User(BaseModel):
    user_id: int
    email: EmailStr

    class Config:
        orm_mode = True
