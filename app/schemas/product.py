from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.schemas.enums import ProductUnit


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


class ProductPublic(ProductBase):
    id: UUID
