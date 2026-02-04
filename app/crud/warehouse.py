from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends

from app.crud.connector import Connector
from app.crud.inventory_oprations import InventoryOperationsCRUD, get_inventory_operations_crud
from app.db.models import Warehouse


class WarehouseCRUD(Connector):
    def __init__(self):
        super().__init__(Warehouse)
