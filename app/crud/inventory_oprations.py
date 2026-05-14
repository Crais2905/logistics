from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.connector import Connector
from app.crud.product import ProductCRUD
from app.crud.stock import StockCRUD, get_stock_crud
from app.crud.warehouse import WarehouseCRUD
from app.db.models import InventoryOperation, Warehouse, Product
from app.schemas.enums.enums import TransferType
from app.schemas.rout_schemas.inventory_operations import InventoryOperationCreate
from app.schemas.rules.inventory_operations import OPERATION_RULES


class InventoryOperationsCRUD(Connector):
    def __init__(self, stock_crud: StockCRUD):
        super().__init__(InventoryOperation)
        self.stock_crud: StockCRUD = stock_crud

    async def create_operation(
        self,
        data: InventoryOperationCreate,
        warehouse_crud: WarehouseCRUD,
        product_crud: ProductCRUD,
        user_id: UUID,
        session: AsyncSession
    ):
        await self._validate_references(data, warehouse_crud, product_crud, session)

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


    async def _validate_references(
            self, data: InventoryOperationCreate,
            warehouse_crud: WarehouseCRUD,
            product_crud: ProductCRUD,
            session: AsyncSession,
    ):
        product = await product_crud.get_object_by_unic_field(
            field_value=data.product_id,
            field=Product.id,
            session=session
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id={data.product_id} not found"
            )

        rule = OPERATION_RULES[data.type]
        warehouse_ids_to_check = {
            "from_warehouse_id": data.from_warehouse_id,
            "to_warehouse_id": data.to_warehouse_id,
        }

        for field, warehouse_id in warehouse_ids_to_check.items():
            if field not in rule.required:
                continue

            warehouse = await warehouse_crud.get_object_by_unic_field(
                field_value=warehouse_id,
                field=Warehouse.id,
                session=session
            )
            if not warehouse:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Warehouse with id={warehouse_id} not found"
                )


def get_inventory_operations_crud(
    stock_crud: StockCRUD = Depends(get_stock_crud),
) -> InventoryOperationsCRUD:
    return InventoryOperationsCRUD(
        stock_crud=stock_crud,
    )
