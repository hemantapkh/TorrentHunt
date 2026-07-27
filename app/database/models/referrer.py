from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.models.base import Base


class Referrer(Base):
    __tablename__ = "referrers"

    referrer_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    clicks: Mapped[int] = mapped_column(default=0)
    date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(),
    )
