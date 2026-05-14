from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends

from app.crud.connector import Connector
from app.db.models import Warehouse


class WarehouseCRUD(Connector):
    def __init__(self):
        super().__init__(Warehouse)

    async def get_operations_by_warehouse_id(
        self,
        warehouse_id: UUID,
        session: AsyncSession,
        desc: Optional[bool] = False,
        offset: int = 0,
        limit: int = 10,
    ):
        warehouse = await self.get_object_by_unic_field(warehouse_id, Warehouse.id, session)

        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
            )

        return await self.get_warehouse_operations(
            warehouse, session, offset, limit, desc_=desc
        )

    async def get_warehouse_operations(
        self, warehouse: Warehouse,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 10,
        desc_: bool = False
    ):
        stmt = select(self.model).filter(
            or_(
                self.model.from_warehouse_id == warehouse.id,
                self.model.to_warehouse_id == warehouse.id
            )
        )

        if desc_:
            stmt = stmt.order_by(desc(self.model.created_at))

        stmt = stmt.offset(offset).limit(limit)
        return await session.scalars(stmt)
