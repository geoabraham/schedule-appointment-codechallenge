import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import null, text
from sqlalchemy.sql.sqltypes import TIMESTAMP, Integer

from .database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    # id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    appointment_id = Column(
        "appointment_id",
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    appointment_date = Column(
        "appointment_date", TIMESTAMP(timezone=True), nullable=False
    )
    user_id = Column("user_id", Integer, nullable=False)
    created_at = Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
