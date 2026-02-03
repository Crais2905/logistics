from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict

from app.schemas.enums.enums import TransferType
from app.schemas.rules.inventory_operations import OPERATION_RULES


class InventoryOperationCreate(BaseModel):
    type: TransferType
    product_id: UUID
    quantity: float = Field(gt=0)
    created_by: Optional[UUID] = None

    from_warehouse_id: Optional[UUID] = None
    to_warehouse_id: Optional[UUID] = None
    comment: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def validate_against_rules(self):
        rule = OPERATION_RULES[self.type]
        data = self.model_dump()

        for field in rule.required:
            if not data.get(field):
                raise ValueError(f"{self.type} requires {field}")

        for field in rule.forbidden:
            if data.get(field):
                raise ValueError(f"{self.type} forbids {field}")

        if self.from_warehouse_id == self.to_warehouse_id:
            raise ValueError("Warehouses must be different")

        return self
