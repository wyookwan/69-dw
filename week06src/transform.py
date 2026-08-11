import pandas as pd
from .config import PROVINCE_MAP

def transform_data(raw):
    """
    TODO 2

    Customers:
    - remove duplicate customer_id
    - standardize province
    - handle missing province/email

    Products:
    - flatten nested JSON fields
    - rename fields
    - convert price to numeric
    - fill missing category with "Unknown"

    Orders:
    - remove duplicate order_id
    - parse mixed date formats
    - normalize status
    - reject invalid records:
        qty <= 0
        unit_price <= 0
        discount_pct < 0 or > 100
        invalid order_date

    Merge:
    - keep paid/completed orders
    - join customers + products
    - reject unknown customer/product

    Calculate:
        gross_amount = qty * unit_price
        discount_amount = gross_amount * discount_pct / 100
        sales_amount = gross_amount - discount_amount

    Return:
        clean_customers,
        clean_products,
        sales,
        rejects
    """
    raise NotImplementedError
