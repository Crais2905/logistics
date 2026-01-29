from pydantic import BaseModel
from uuid import  UUID


class WarehouseBase(BaseModel):
    name: str
    location: str


class WarehouseCreate(WarehouseBase):
    pass


class WarehousePublic(WarehouseBase):
    id: UUID
    is_active: bool
