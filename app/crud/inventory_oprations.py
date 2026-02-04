from uuid import UUID

import asyncio
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.crud.connector import Connector
from app.crud.stock import StockCRUD, get_stock_crud
from app.db.models import InventoryOperation
from app.schemas.enums.enums import TransferType
from app.schemas.rout_schemas.inventory_operations import InventoryOperationCreate


class InventoryOperationsCRUD(Connector):
    def __init__(self, stock_crud: StockCRUD):
        super().__init__(InventoryOperation)
        self.stock_crud: StockCRUD = stock_crud

    async def create_operation(
        self,
        data: InventoryOperationCreate,
        user_id: UUID,
        session: AsyncSession
    ):
        data = InventoryOperationCreate(
            **data.model_dump(exclude={"created_by"}),
            created_by=user_id
        )

        operation = await self.write_to_db(data, session, commit=False)
        try:
            await self._apply_stock_changes(operation, session)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}"
            )

        await session.commit()
        return operation

    async def _apply_stock_changes(
        self,
        operation: InventoryOperation,
        session: AsyncSession
    ):
        qty = operation.quantity

        match operation.type:
            case TransferType.INBOUND.value:
                await self.stock_crud.increase(
                    product_id=operation.product_id,
                    warehouse_id=operation.to_warehouse_id,
                    quantity=qty,
                    session=session,
                )

            case TransferType.OUTBOUND.value:
                await self.stock_crud.decrease(
                    product_id=operation.product_id,
                    warehouse_id=operation.from_warehouse_id,
                    quantity=qty,
                    session=session,
                )

            case TransferType.TRANSFER.value:
                await self.stock_crud.decrease(
                    operation.product_id,
                    operation.from_warehouse_id,
                    qty,
                    session=session,
                )
                await self.stock_crud.increase(
                    operation.product_id,
                    operation.to_warehouse_id,
                    qty,
                    session=session,
                )

            case TransferType.ADJUSTMENT.value:
                await self.stock_crud.adjust(
                    operation.product_id,
                    operation.from_warehouse_id,
                    qty,
                    session=session,
                )


def get_inventory_operations_crud(
    stock_crud: StockCRUD = Depends(get_stock_crud),
) -> InventoryOperationsCRUD:
    return InventoryOperationsCRUD(stock_crud=stock_crud)