import uuid
from typing import List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship, validates
from sqlalchemy import String, Integer, ForeignKey, Boolean, UUID, DateTime, Enum, Numeric, Text

from app.schemas.enums.enums import UserRole


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
    operations: Mapped[List["InventoryOperation"]] = relationship(
        "InventoryOperation", back_populates="creator"
    )


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
    outgoing_movements = relationship(
        "InventoryOperation",
        foreign_keys="InventoryOperation.from_warehouse_id",
        back_populates="from_warehouse"
    )

    incoming_movements = relationship(
        "InventoryOperation",
        foreign_keys="InventoryOperation.to_warehouse_id",
        back_populates="to_warehouse"
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
    operations: Mapped[List["InventoryOperation"]] = relationship(
        "InventoryOperation", back_populates="product", cascade="all, delete-orphan"
    )


class Stock(Base):
    __tablename__ = 'stock'

    product_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('product.id'), primary_key=True)
    product: Mapped[Product] = relationship("Product", back_populates="stocks", lazy="selectin")

    warehouse_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('warehouse.id'), primary_key=True)
    warehouse: Mapped[Warehouse] = relationship("Warehouse", back_populates="stocks", lazy="selectin")

    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    @validates("quantity")
    def validate_quantity(self, key, value):
        if value < 0:
            raise ValueError("Quantity must be greater or equal than 0")
        return value


class InventoryOperation(Base):
    __tablename__ = 'inventory_operation'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    product_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('product.id'))
    product: Mapped[Product] = relationship("Product", back_populates="operations", lazy="selectin")

    from_warehouse_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('warehouse.id'), nullable=True)
    from_warehouse: Mapped[Warehouse] = relationship(
        "Warehouse",
        foreign_keys=[from_warehouse_id],
        back_populates="outgoing_movements"
    )

    to_warehouse_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('warehouse.id'), nullable=True)
    to_warehouse: Mapped[Warehouse] = relationship(
        "Warehouse",
        foreign_keys=[to_warehouse_id],
        back_populates="incoming_movements"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    created_by: Mapped[UUID] = mapped_column(UUID, ForeignKey('user.id'))
    creator: Mapped[User] = relationship("User", back_populates="operations", lazy="selectin")

    comment: Mapped[str] = mapped_column(Text, nullable=True)
