from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.crud.product import ProductCRUD
from app.crud.warehouse import WarehouseCRUD
from app.schemas.enums.enums import UserRole
from app.schemas.rout_schemas.inventory_operations import InventoryOperationCreate
from app.crud.inventory_oprations import get_inventory_operations_crud, InventoryOperationsCRUD
from app.db.session import get_session
from app.schemas.rout_schemas.user import UserPublic

router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK)
async def create_operation(
    data: InventoryOperationCreate,
    inventory_operations_crud: InventoryOperationsCRUD = Depends(get_inventory_operations_crud),
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD),
    product_crud: ProductCRUD = Depends(ProductCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(
        UserRole.admin,
        UserRole.manager
    ))
):
    result = await inventory_operations_crud.create_operation(
        data,
        warehouse_crud,
        product_crud,
        current_user.id,
        session
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error while creating new operation"
        )

    return {"detail": "Operations successfully created"}