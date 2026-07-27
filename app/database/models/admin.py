from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.models.base import Base


class Admin(Base):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(),
    )
