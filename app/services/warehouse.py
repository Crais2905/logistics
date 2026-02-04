from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.inventory_oprations import InventoryOperationsCRUD
from app.crud.warehouse import WarehouseCRUD
from app.db.models import Warehouse
from app.schemas.rout_schemas.warehouse import WarehouseUpdate, WarehouseCreate


class WarehouseService:
    def __init__(self, warehouse_crud: WarehouseCRUD):
        self.warehouse_crud: WarehouseCRUD = warehouse_crud
        self.model = Warehouse

    async def get_warehouses(
            self, session: AsyncSession,
            offset: int,
            limit: int
    ):
        if offset < 0 or limit < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="offset and limit must be greater than 0"
            )

        return await self.warehouse_crud.get_objects(session, offset, limit)

    async def get_warehouse(
            self, warehouse_id: UUID,
            session: AsyncSession
    ):
        warehouse = await self.warehouse_crud.get_object_by_unic_field(
            warehouse_id, Warehouse.id, session
        )

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found"
            )

        return warehouse

    async def create_warehouse(
        self, session: AsyncSession,
            data: WarehouseCreate
    ):
        warehouse = await self.warehouse_crud.get_object_by_unic_field(
            data.name, Warehouse.name, session
        )

        if warehouse:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This name already exist"
            )

        return await self.warehouse_crud.write_to_db(data, session)

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
    
    async def deactivate_warehouse(
        self, warehouse_id: UUID,
        session: AsyncSession
    ):
        warehouse = await self.warehouse_crud.get_object_by_unic_field(
            warehouse_id,
            Warehouse.id,
            session
        )

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found"
            )

        await self.warehouse_crud.deactivate_object(warehouse_id, session)
        return warehouse

    async def update_warehouse(
        self, warehouse_id: UUID,
        session: AsyncSession,
        new_data: WarehouseUpdate
    ):
        warehouse = await self.warehouse_crud.get_object_by_unic_field(
            warehouse_id,
            Warehouse.id,
            session
        )

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found"
            )

        if not warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Warehouse isn't active"
            )

        return await self.warehouse_crud.update_object(warehouse_id, new_data, session)


def get_warehouse_service(
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD)
) -> WarehouseService:
    return WarehouseService(warehouse_crud=warehouse_crud)
