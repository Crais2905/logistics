from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.warehouse import WarehouseCreate, WarehousePublic, WarehouseUpdate
from app.schemas.user import UserPublic
from app.crud.warehouse import WarehouseCRUD
from app.auth.dependencies import get_current_user, require_role
from app.db.session import get_session
from app.db.models import Warehouse
from app.schemas.enums import UserRole

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WarehousePublic)
async def create_warehouse(
    data: WarehouseCreate,
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(
        UserRole.admin,
        UserRole.manager
    ))
):
    warehouse = await warehouse_crud.get_object_by_unic_field(
        data.name, Warehouse.name, session
    )

    if warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This name already exist"
        )

    return await warehouse_crud.write_to_db(data, session)


@router.get("/{warehouse_id}", status_code=status.HTTP_200_OK, response_model=WarehousePublic)
async def get_warehouse(
    warehouse_id: UUID,
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD),
    session: AsyncSession = Depends(get_session)
):
    warehouse = await warehouse_crud.get_object_by_unic_field(
        warehouse_id, Warehouse.id, session
    )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    return warehouse


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[WarehousePublic])
async def get_warehouses(
    offset: int = 0,
    limit: int = 5,
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD),
    session: AsyncSession = Depends(get_session)
):
    return await warehouse_crud.get_objects(session, offset, limit)


@router.patch("/{warehouse_id}", status_code=status.HTTP_200_OK, response_model=WarehousePublic)
async def update_warehouse(
    warehouse_id: UUID,
    new_data: WarehouseUpdate,
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(
        UserRole.admin, UserRole.manager
    ))
):
    warehouse = await warehouse_crud.get_object_by_unic_field(
        warehouse_id,
        Warehouse.id,
        session
    )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    return await warehouse_crud.update_object(warehouse_id, new_data, session)


@router.patch("/{warehouse_id}/deactivate", status_code=status.HTTP_200_OK, response_model=WarehousePublic)
async def warehouse_deactivate(
    warehouse_id: UUID,
    warehouse_crud: WarehouseCRUD = Depends(WarehouseCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(UserRole.admin))
):
    warehouse = await warehouse_crud.get_object_by_unic_field(
        warehouse_id,
        Warehouse.id,
        session
    )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    warehouse.is_active = False
    await session.commit()
    await session.refresh(warehouse)

    return warehouse
