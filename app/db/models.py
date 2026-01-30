import uuid
from typing import List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship, validates
from sqlalchemy import String, Integer, ForeignKey, Boolean, UUID, DateTime, Enum, Numeric

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


class Warehouse(Base):
    __tablename__ = 'warehouse'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    stocks: Mapped[List["Stock"]] = relationship(
        "Stock", back_populates="warehouse", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(256), nullable=False)
    unit: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    stocks: Mapped[List["Stock"]] = relationship(
        "Stock", back_populates="product", cascade="all, delete-orphan"
    )


class Stock(Base):
    __tablename__ = 'stock'

    product_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('product.id'), primary_key=True)
    product: Mapped[Product] = relationship("Product", back_populates="stocks", lazy="selectin")

    warehouse_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('warehouse.id'), primary_key=True)
    warehouse: Mapped[Warehouse] = relationship("Warehouse", back_populates="stocks", lazy="selectin")

    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, )
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    @validates("quantity")
    def validate_quantity(self, key, value):
        if value < 0:
            raise ValueError("Quantity must be greater or equal than 0")
        return value
