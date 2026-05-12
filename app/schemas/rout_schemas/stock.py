from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.rout_schemas.product import ProductPublic
from app.schemas.rout_schemas.warehouse import WarehousePublic


class StockBase(BaseModel):
    quantity: float
    updated_at: datetime


class StockCreate(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity: float


class StockPublic(StockBase):
    product: ProductPublic
    warehouse: WarehousePublic
