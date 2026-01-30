from app.crud.connector import Connector
from app.db.models import Stock


class StockCRUD(Connector):
    def __init__(self):
        super().__init__(Stock)
