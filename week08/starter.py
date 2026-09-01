from pathlib import Path
import json
import pandas as pd

DATA = Path(__file__).parent / "data"
OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

# TODO 1: Extract ข้อมูลจาก CSV, Excel และ JSON
# TODO 2: ทำ schema alignment ของไฟล์ orders สองเดือน แล้ว concat
# TODO 3: Clean/standardize/deduplicate และสร้าง data quality report
# TODO 4: Enrich ด้วย customer, product และ payment master
# TODO 5: Validate business rules ก่อนคำนวณยอดขาย
# TODO 6: Load dim_customer.csv, dim_product.csv และ fact_sales.csv
# TODO 7: สร้าง summary_by_province.csv และ summary_by_category.csv

print("เริ่มทำ Data Integration ได้เลย")
