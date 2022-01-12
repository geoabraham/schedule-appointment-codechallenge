import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP, Integer, String

from .database import Base


class Appointment(Base):
    __tablename__ = "appointments"

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

    user_id = Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class User(Base):
    __tablename__ = "users"

    user_id = Column("user_id", Integer, nullable=False, primary_key=True)

    email = Column("email", String, nullable=False, unique=True)

    user_passwd = Column("user_passwd", String, nullable=False)

    created_at = Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
