from datetime import datetime
from pydantic import BaseModel

from app.schemas.product import ProductPublic
from app.schemas.warehouse import WarehousePublic


class StockBase(BaseModel):
    quantity: float
    updated_at: datetime


class StockPublic(BaseModel):
    product: ProductPublic
    warehouse: WarehousePublic
