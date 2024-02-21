import datetime
import uuid

from sqlalchemy import Boolean, String, DateTime
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from worklog.database.base_class import Base


class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(254), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r}, is_active={self.is_active!r})"