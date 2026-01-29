from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import ProductCreate, ProductUpdate, ProductPublic
from app.schemas.user import UserPublic
from app.crud.product import ProductCRUD
from app.auth.dependencies import get_current_user, require_role
from app.db.session import get_session
from app.db.models import Product
from app.schemas.enums import UserRole

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductPublic)
async def create_product(
    product_data: ProductCreate,
    product_crud: ProductCRUD = Depends(ProductCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(UserRole.admin, UserRole.manager))
):
    product = await product_crud.get_object_by_unic_field(
        product_data.name, Product.name, session
    )

    if product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This name already exist"
        )

    return await product_crud.write_to_db(product_data, session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[ProductPublic])
async def get_products(
    offset: int = 0,
    limit: int = 10,
    product_crud: ProductCRUD = Depends(ProductCRUD),
    session: AsyncSession = Depends(get_session)
):
    return await product_crud.get_objects(session, offset, limit)


@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductPublic)
async def get_product(
    product_id: UUID,
    product_crud: ProductCRUD = Depends(ProductCRUD),
    session: AsyncSession = Depends(get_session)
):
    product = await product_crud.get_object_by_unic_field(
        product_id, Product.id, session
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.patch("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductPublic)
async def update_warehouse(
    product_id: UUID,
    new_data: ProductUpdate,
    product_crud: ProductCRUD = Depends(ProductCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(
        UserRole.admin, UserRole.manager
    ))
):
    product = await product_crud.get_object_by_unic_field(
        product_id,
        Product.id,
        session
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product isn't active"
        )

    return await product_crud.update_object(product_id, new_data, session)


@router.patch("/{product_id}/deactivate", status_code=status.HTTP_200_OK, response_model=ProductPublic)
async def warehouse_deactivate(
    product_id: UUID,
    product_crud: ProductCRUD = Depends(ProductCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(UserRole.admin))
):
    product = await product_crud.get_object_by_unic_field(
        product_id,
        Product.id,
        session
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    await product_crud.deactivate_object(product_id, session)
    return product
