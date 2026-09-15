from pathlib import Path
import sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parent
with sqlite3.connect((ROOT/'data'/'warehouse.db').as_uri()+'?mode=ro',uri=True) as con:
    df=pd.read_sql_query('SELECT * FROM sales',con)
print(df.head())
# TODO P1: province x month, sum(amount), fill_value=0, margins=True
# TODO P2: filter September, then category x province
# TODO P3: assert that the pivot grand total equals df['amount'].sum()
# TODO P4: export each result to CSV in your submission folder
