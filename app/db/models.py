import uuid
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, UUID, DateTime, Enum

from app.schemas.enums import UserRole


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    firstname: Mapped[str] = mapped_column(String(256), nullable=False)
    lastname: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, default=UserRole.viewer.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
