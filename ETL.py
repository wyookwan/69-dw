from __future__ import annotations

from pathlib import Path
import re
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "workshop" / "raw_ecommerce_data.csv"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DB_PATH = OUTPUT_DIR / "warehouse.db"

"""ETL Pipeline ฉบับสมบูรณ์สำหรับ Instructor Demo

ลำดับ: Extract -> Transform Dimensions -> Transform Fact -> Create Schema -> Load -> Verify
"""


def clean_text(value: object, default: str = "Unknown") -> str:
    if pd.isna(value) or str(value).strip() == "":
        return default
    return " ".join(str(value).strip().split()).title()


def clean_email(value: object) -> str:
    return "" if pd.isna(value) else str(value).strip().lower()


def clean_number(value: object) -> float | None:
    if pd.isna(value) or str(value).strip() == "":
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", str(value))
    return float(cleaned) if cleaned else None


def parse_mixed_date(value: object) -> pd.Timestamp:
    text = "" if pd.isna(value) else str(value).strip()
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"]:
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        if not pd.isna(parsed):
            return parsed
    return pd.NaT


def extract() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype=str, encoding="utf-8-sig")
    df.columns = [c.strip().lower() for c in df.columns]
    print(f"[Extract] raw rows={len(df):,}, duplicate order_id={df.duplicated('order_id').sum():,}")
    return df


def transform(df: pd.DataFrame):
    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    df["customer_name"] = df["customer_name"].apply(clean_text)
    df["email"] = df["email"].apply(clean_email)
    df.loc[df["email"].eq(""), "email"] = (
        df.loc[df["email"].eq(""), "customer_name"]
          .str.lower().str.replace(r"[^a-z0-9]+", ".", regex=True).str.strip(".")
        + "@unknown.local"
    )
    df["product"] = df["product"].apply(clean_text)
    df["category"] = df["category"].apply(clean_text)
    df["order_date"] = df["order_date"].apply(parse_mixed_date)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = df["unit_price"].apply(clean_number)
    df["amount"] = df["amount"].apply(clean_number)
    df["amount"] = df["amount"].fillna(df["quantity"] * df["unit_price"])
    df = df.dropna(subset=["order_date", "unit_price", "amount"])
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)].copy()

    customer_candidates = df[["customer_name", "email"]].copy()
    customer_candidates["_unknown_name"] = customer_candidates["customer_name"].eq("Unknown")
    dim_customer = (customer_candidates.sort_values(["email", "_unknown_name", "customer_name"])
                    .drop_duplicates("email").drop(columns="_unknown_name")
                    .sort_values(["customer_name", "email"]).reset_index(drop=True))
    dim_customer.insert(0, "customer_id", range(1, len(dim_customer) + 1))

    product_candidates = df[["product", "category"]].copy()
    product_candidates["_unknown_category"] = product_candidates["category"].eq("Unknown")
    dim_product = (product_candidates.sort_values(["product", "_unknown_category", "category"])
                   .drop_duplicates("product").drop(columns="_unknown_category")
                   .sort_values(["category", "product"]).reset_index(drop=True)
                   .rename(columns={"product": "product_name"}))
    dim_product.insert(0, "product_id", range(1, len(dim_product) + 1))

    dim_date = df[["order_date"]].drop_duplicates().sort_values("order_date").reset_index(drop=True).rename(columns={"order_date": "full_date"})
    dim_date["date_id"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["quarter"] = "Q" + dim_date["full_date"].dt.quarter.astype(str)
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date = dim_date[["date_id", "full_date", "day", "month", "month_name", "quarter", "year"]]

    mapped = df.merge(dim_customer[["customer_id", "email"]], on="email", how="left", validate="many_to_one")
    mapped = mapped.merge(dim_product[["product_id", "product_name"]], left_on="product", right_on="product_name", how="left", validate="many_to_one")
    mapped = mapped.merge(dim_date[["date_id", "full_date"]], left_on="order_date", right_on="full_date", how="left", validate="many_to_one")

    fact_sales = mapped[["order_id", "customer_id", "product_id", "date_id", "quantity", "unit_price", "amount"]].rename(
        columns={"order_id": "transaction_id", "amount": "total_amount"}
    )
    fact_sales[["customer_id", "product_id", "date_id"]] = fact_sales[["customer_id", "product_id", "date_id"]].astype(int)
    fact_sales["total_amount"] = fact_sales["total_amount"].round(2)
    print(f"[Transform] customers={len(dim_customer)}, products={len(dim_product)}, dates={len(dim_date)}, facts={len(fact_sales)}")
    return dim_customer, dim_product, dim_date, fact_sales


def load(dim_customer, dim_product, dim_date, fact_sales):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript("""
        DROP TABLE IF EXISTS fact_sales;
        DROP TABLE IF EXISTS dim_customer;
        DROP TABLE IF EXISTS dim_product;
        DROP TABLE IF EXISTS dim_date;
        CREATE TABLE dim_customer (customer_id INTEGER PRIMARY KEY, customer_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE);
        CREATE TABLE dim_product (product_id INTEGER PRIMARY KEY, product_name TEXT NOT NULL, category TEXT NOT NULL, UNIQUE(product_name, category));
        CREATE TABLE dim_date (date_id INTEGER PRIMARY KEY, full_date TEXT NOT NULL UNIQUE, day INTEGER NOT NULL, month INTEGER NOT NULL, month_name TEXT NOT NULL, quarter TEXT NOT NULL, year INTEGER NOT NULL);
        CREATE TABLE fact_sales (
            transaction_id TEXT PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES dim_customer(customer_id),
            product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
            date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            total_amount REAL NOT NULL CHECK(total_amount >= 0)
        );
        """)
        dim_customer.to_sql("dim_customer", conn, if_exists="append", index=False)
        dim_product.to_sql("dim_product", conn, if_exists="append", index=False)
        dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
        fact_sales.to_sql("fact_sales", conn, if_exists="append", index=False)
        conn.commit()
    print(f"[Load] database={DB_PATH}")


def verify():
    sql = """
    SELECT c.customer_name, ROUND(SUM(f.total_amount), 2) AS total_spend
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    GROUP BY c.customer_id, c.customer_name
    ORDER BY total_spend DESC
    LIMIT 5;
    """
    with sqlite3.connect(DB_PATH) as conn:
        result = pd.read_sql_query(sql, conn)
    print("[Verify] Top 5 customers")
    print(result.to_string(index=False))


if __name__ == "__main__":
    raw = extract()
    dimensions_and_fact = transform(raw)
    load(*dimensions_and_fact)
    verify()
    print("ETL Pipeline run successfully!")
