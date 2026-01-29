from app.crud.connector import Connector
from app.db.models import Product


class ProductCRUD(Connector):
    def __init__(self):
        super().__init__(Product)
