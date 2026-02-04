from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.connector import Connector
from app.db.models import Stock


class StockCRUD(Connector):
    def __init__(self):
        super().__init__(Stock)

    async def get_stock(
        self,
        product_id: UUID,
        warehouse_id: UUID,
        session: AsyncSession,
    ):
        stmt = select(self.model).where(
            self.model.product_id == product_id,
            self.model.warehouse_id == warehouse_id,
        ).with_for_update()

        return await session.scalar(stmt)

    async def increase(
            self,
            product_id: UUID,
            warehouse_id: UUID,
            quantity: float,
            session: AsyncSession
    ):
        stock = await self.get_stock(product_id, warehouse_id, session)
        print("Stock found")
        stock.quantity += quantity
        print(f"Stock increase on {quantity}")

    async def decrease(
            self,
            product_id: UUID,
            warehouse_id: UUID,
            quantity: float,
            session: AsyncSession
    ):
        stock = await self.get_stock(product_id, warehouse_id, session)

        if stock.quantity < quantity:
            raise ValueError("Insufficient stock")

        stock.quantity -= quantity

    async def adjust(
            self,
            product_id: UUID,
            warehouse_id: UUID,
            quantity: float,
            session: AsyncSession
    ):
        stock = await self.get_stock(product_id, warehouse_id, session)
        stock.quantity = quantity


def get_stock_crud() -> StockCRUD:
    return StockCRUD()