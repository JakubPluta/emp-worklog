import datetime
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, validates

from worklog.database.base_class import Base


class Timelog(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False
    )
    date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True), nullable=False)
    hours: Mapped[int] = mapped_column(Integer, nullable=False)
    minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str] = mapped_column(String(254), nullable=True)

    @validates("hours")
    def validate_hours(self, key, value):
        if value < 0:
            raise ValueError("Hours cannot be negative")
        if value > 24:
            raise ValueError("Hours cannot be greater than 24")
        return value

    @validates("minutes")
    def validate_minutes(self, key, value):
        if value < 0:
            raise ValueError("Minutes cannot be negative")
        if value >= 60:
            raise ValueError("Minutes cannot be greater or equal than 60")
        return value
