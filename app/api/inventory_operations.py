from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.schemas.enums.enums import UserRole
from app.schemas.rout_schemas.inventory_operations import InventoryOperationCreate
from app.crud.inventory_oprations import get_inventory_operations_crud, InventoryOperationsCRUD
from app.db.session import get_session
from app.schemas.rout_schemas.user import UserPublic

router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK)
async def get_stocks(
    data: InventoryOperationCreate,
    inventory_operations_crud: InventoryOperationsCRUD = Depends(get_inventory_operations_crud),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(
        UserRole.admin,
        UserRole.manager
    ))
):
    result = await inventory_operations_crud.create_operation(data, current_user.id, session)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error while creating new operation"
        )

    return {"detail": "Operations successfully created"}