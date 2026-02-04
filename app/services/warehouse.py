from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.inventory_oprations import InventoryOperationsCRUD
from app.crud.warehouse import WarehouseCRUD
from app.db.models import Warehouse


class WarehouseService:
    def __init__(self, warehouse_crud: WarehouseCRUD):
        self.warehouse_crud: WarehouseCRUD = warehouse_crud
        self.model = Warehouse

    async def get_operations_by_warehouse_id(
        self,
        warehouse_id: UUID,
        session: AsyncSession,
        inventory_operation_crud: InventoryOperationsCRUD,
        desc: Optional[bool] = False,
        offset: int = 0,
        limit: int = 10,
    ):
        warehouse = await self.warehouse_crud.get_object_by_unic_field(warehouse_id, Warehouse.id, session)

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
            )

        return await inventory_operation_crud.get_warehouse_operations(
            warehouse, session, offset, limit, desc_=desc
        )


def get_warehouse_service(
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD)
) -> WarehouseService:
    return WarehouseService(warehouse_crud=warehouse_crud)
