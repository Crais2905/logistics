from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

from app.schemas.enums.enums import ProductUnit


class ProductBase(BaseModel):
    name: str
    sku: str
    unit: ProductUnit


class ProductCreate(ProductBase):
    model_config = ConfigDict(use_enum_values=True)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[ProductUnit] = None

    model_config = ConfigDict(use_enum_values=True)


class ProductPublic(ProductBase):
    id: UUID
    is_active: bool
    create_at: datetime
