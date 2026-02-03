from dataclasses import dataclass
from typing import Set

from app.schemas.enums.enums import TransferType


@dataclass(frozen=True)
class OperationRule:
    required: Set[str]
    forbidden: Set[str]


OPERATION_RULES = {
    TransferType.INBOUND.value: OperationRule(
        required={"to_warehouse_id"},
        forbidden={"from_warehouse_id"},
    ),
    TransferType.OUTBOUND.value: OperationRule(
        required={"from_warehouse_id"},
        forbidden={"to_warehouse_id"},
    ),
    TransferType.TRANSFER.value: OperationRule(
        required={"from_warehouse_id", "to_warehouse_id"},
        forbidden=set(),
    ),
    TransferType.ADJUSTMENT.value: OperationRule(
        required=set(),
        forbidden={"from_warehouse_id", "to_warehouse_id"},
    ),
}
