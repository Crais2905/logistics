from pydantic import BaseModel
from uuid import UUID


class WarehouseBase(BaseModel):
    name: str
    location: str


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: str | None = None
    location: str | None = None


class WarehousePublic(WarehouseBase):
    id: UUID
    is_active: bool
