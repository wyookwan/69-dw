import sqlite3
from .config import WAREHOUSE_DB

def load_data(customers, products, sales):
    """
    TODO 3

    Create/load these tables:
      dim_customer
      dim_product
      fact_sales

    Requirements:
    - customer_id unique in dim_customer
    - product_id unique in dim_product
    - order_id unique in fact_sales
    - running the pipeline twice must NOT duplicate fact_sales

    Hint:
    Use SQLite UNIQUE constraints and INSERT OR IGNORE / upsert logic.
    """
    raise NotImplementedError
