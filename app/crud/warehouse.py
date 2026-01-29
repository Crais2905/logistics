from app.crud.connector import Connector
from app.db.models import Warehouse


class WarehouseCRUD(Connector):
    def __init__(self):
        super().__init__(Warehouse)

