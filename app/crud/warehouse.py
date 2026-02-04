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

    async def get_operations_by_warehouse_id(
        self,
        warehouse_id: UUID,
        session: AsyncSession,
        inventory_operation_crud: InventoryOperationsCRUD,
        desc: Optional[bool] = False,
        offset: int = 0,
        limit: int = 10,
    ):
        warehouse = await self.get_object_by_unic_field(warehouse_id, Warehouse.id, session)

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
            )

        return await inventory_operation_crud.get_warehouse_operations(
            warehouse, session, offset, limit, desc_=desc
        )
