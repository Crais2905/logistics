from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.rout_schemas.warehouse import WarehouseCreate, WarehousePublic, WarehouseUpdate
from app.schemas.rout_schemas.user import UserPublic
from app.schemas.rout_schemas.inventory_operations import InventoryOperationsPublic
from app.crud.warehouse import WarehouseCRUD
from app.crud.inventory_oprations import InventoryOperationsCRUD, get_inventory_operations_crud
from app.auth.dependencies import require_role
from app.db.session import get_session
from app.db.models import Warehouse
from app.schemas.enums.enums import UserRole
from app.services.warehouse import WarehouseService, get_warehouse_service

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WarehousePublic)
async def create_warehouse(
    data: WarehouseCreate,
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(
        UserRole.admin,
        UserRole.manager
    ))
):
    return await warehouse_service.create_warehouse(session, data)


@router.get("/{warehouse_id}", status_code=status.HTTP_200_OK, response_model=WarehousePublic)
async def get_warehouse(
    warehouse_id: UUID,
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    session: AsyncSession = Depends(get_session)
):
    return await warehouse_service.get_warehouse(warehouse_id, session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[WarehousePublic])
async def get_warehouses(
    offset: int = 0,
    limit: int = 5,
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    session: AsyncSession = Depends(get_session)
):
    return await warehouse_service.get_warehouses(session, offset, limit)


@router.patch("/{warehouse_id}", status_code=status.HTTP_200_OK, response_model=WarehousePublic)
async def update_warehouse(
    warehouse_id: UUID,
    new_data: WarehouseUpdate,
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(
        UserRole.admin, UserRole.manager
    ))
):
    return await warehouse_service.update_warehouse(warehouse_id, session, new_data)


@router.patch("/{warehouse_id}/deactivate", status_code=status.HTTP_200_OK, response_model=WarehousePublic)
async def warehouse_deactivate(
    warehouse_id: UUID,
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(UserRole.admin))
):
    return await warehouse_service.deactivate_warehouse(warehouse_id, session)


@router.get("/{warehouse_id}/operations", status_code=status.HTTP_200_OK, response_model=List[InventoryOperationsPublic])
async def get_warehouse_operations(
    warehouse_id: UUID,
    offset: int = 0,
    limit: int = 10,
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    inventory_operations_crud: InventoryOperationsCRUD = Depends(get_inventory_operations_crud),
    session: AsyncSession = Depends(get_session),
):
    return await warehouse_service.get_operations_by_warehouse_id(
        warehouse_id, session, inventory_operations_crud, offset=offset, limit=limit, desc=True
    )
