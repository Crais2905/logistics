from typing import Optional
from uuid import UUID

from fastapi import Query

from app.db.models import Stock


def stock_filters(
    product_id: Optional[UUID] = Query(None, description="Filter by product id"),
    warehouse_id: Optional[UUID] = Query(None, description="Filter by warehouse id"),
    zero_quantity: Optional[bool] = Query(False, description="Give products were quantity equal 0"),
    active_warehouse: Optional[bool] = Query(True, description="Give products only in active warehouses")
):
    filters = []

    if product_id:
        filters.append(Stock.product_id == product_id)
    if warehouse_id:
        filters.append(Stock.warehouse_id == warehouse_id)
    if zero_quantity:
        filters.append(Stock.quantity == 0)
    if active_warehouse:
        filters.append(Stock.warehouse.has(is_active=True))

    return filters
