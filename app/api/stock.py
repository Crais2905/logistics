from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.rout_schemas.stock import StockPublic
from app.utils.stock_filters import stock_filters
from app.crud.stock import StockCRUD
from app.db.session import get_session

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[StockPublic])
async def get_stocks(
    offset: int = 0,
    limit: int = 10,
    filters: list = Depends(stock_filters),
    stock_crud: StockCRUD = Depends(StockCRUD),
    session: AsyncSession = Depends(get_session)
):
    if offset < 0 or limit < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="offset and limit must be greater than 0"
        )

    return await stock_crud.get_objects(session, offset, limit, filters)


