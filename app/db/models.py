from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, UUID, DateTime

from app.schemas.enums import UserRole


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id: Mapped[uuid4] = mapped_column(UUID, primary_key=True)
    firstname: Mapped[str] = mapped_column(String(256), nullable=False)
    lastname: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(String, default=UserRole.viewer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)