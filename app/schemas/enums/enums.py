from enum import Enum


class UserRole(Enum):
    admin = "admin"
    manager = "manager"
    viewer = "viewer"


class ProductUnit(Enum):
    pcs = "pcs"
    kg = "kg"
    l = "l"
    m = "m"


class TransferType(Enum):
    INBOUND = 'inbound'
    OUTBOUND = 'outbound'
    TRANSFER = 'transfer'
    ADJUSTMENT = 'adjustment'
