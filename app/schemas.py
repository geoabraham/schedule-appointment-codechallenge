from datetime import datetime
from pydantic.types import UUID4

from pydantic.main import BaseModel


class BaseAppointment(BaseModel):
    appointment_date: datetime
    user_id: int


class CreateAppointment(BaseAppointment):
    pass


class UpdateAppointment(BaseAppointment):
    pass


class Appointment(BaseAppointment):
    appointment_id: UUID4

    class Config:
        orm_mode = True
