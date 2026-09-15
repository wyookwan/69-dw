"""Create isolated teaching databases. Run: python lab.py [--reset]."""
from pathlib import Path
import sqlite3, csv, random, argparse
from datetime import date, timedelta
ROOT = Path(__file__).resolve().parent
SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE dim_date(date_key INTEGER PRIMARY KEY, full_date TEXT NOT NULL UNIQUE, year INTEGER NOT NULL, month TEXT NOT NULL);
CREATE TABLE dim_product(product_key INTEGER PRIMARY KEY, product_name TEXT NOT NULL, category TEXT NOT NULL);
CREATE TABLE dim_store(store_key INTEGER PRIMARY KEY, store_name TEXT NOT NULL, province TEXT NOT NULL, region TEXT NOT NULL);
CREATE TABLE fact_sales(order_id TEXT NOT NULL, line_no INTEGER NOT NULL CHECK(line_no>0), date_key INTEGER NOT NULL REFERENCES dim_date, product_key INTEGER NOT NULL REFERENCES dim_product, store_key INTEGER NOT NULL REFERENCES dim_store, quantity INTEGER NOT NULL CHECK(quantity>0), unit_price INTEGER NOT NULL CHECK(unit_price>=0), PRIMARY KEY(order_id,line_no));
CREATE VIEW sales AS SELECT f.order_id,f.line_no,d.full_date,d.year,d.month,p.product_name,p.category,s.store_name,s.province,s.region,f.quantity,f.unit_price,f.quantity*f.unit_price AS amount FROM fact_sales f JOIN dim_date d ON f.date_key=d.date_key JOIN dim_product p ON f.product_key=p.product_key JOIN dim_store s ON f.store_key=s.store_key;
'''
PRODUCTS=[(1,'Tea','Drink',50),(2,'Cookie','Snack',80),(3,'Coffee','Drink',65),(4,'Cocoa','Drink',60),(5,'Brownie','Snack',90),(6,'Sandwich','Food',100)]
STORES=[(1,'Bangsaen','Chonburi','East'),(2,'Siam','Bangkok','Central'),(3,'Pattaya','Chonburi','East'),(4,'Ari','Bangkok','Central'),(5,'Muang Rayong','Rayong','East'),(6,'Nimman','Chiang Mai','North')]
def write_csv(path,headers,rows):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(headers); w.writerows(rows)
def make_db(path,rows,extended=False):
    if path.exists(): path.unlink()
    con=sqlite3.connect(path); con.executescript(SCHEMA)
    dates=sorted({r[2] for r in rows})
    con.executemany('INSERT INTO dim_date VALUES (?,?,?,?)',[(k,f'{k//10000:04}-{k//100%100:02}-{k%100:02}',k//10000,f'{k//10000:04}-{k//100%100:02}') for k in dates])
    con.executemany('INSERT INTO dim_product VALUES (?,?,?)',[p[:3] for p in PRODUCTS[:6 if extended else 2]])
    con.executemany('INSERT INTO dim_store VALUES (?,?,?,?)',STORES[:6 if extended else 2])
    con.executemany('INSERT INTO fact_sales VALUES (?,?,?,?,?,?,?)',rows); con.commit()
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    q=con.execute('SELECT * FROM sales ORDER BY order_id,line_no')
    write_csv(path.with_suffix('.csv'),[c[0] for c in q.description],q.fetchall())
    con.close()
def main():
    args=argparse.ArgumentParser();args.add_argument('--reset',action='store_true',help='Recreate supplied lab databases and CSVs; save your changes first.')
    a=args.parse_args(); data=ROOT/'data';data.mkdir(exist_ok=True)
    targets=[data/'warehouse.db',data/'extended.db',data/'oltp.db']
    if any(p.exists() for p in targets) and not a.reset:
        print('Prepared data already exists. Use --reset only to discard lab data changes.');return
    base=[('O1001',1,20260808,1,1,2,50),('O1001',2,20260808,2,1,1,80),('O1002',1,20260809,1,2,3,50),('O1003',1,20260810,2,2,2,80),('O1004',1,20260909,1,1,4,50),('O1004',2,20260909,2,1,2,80),('O1005',1,20260910,1,2,6,50),('O1006',1,20260911,2,2,3,80)]
    make_db(targets[0],base)
    rng=random.Random(9033267); rows=[]
    for i in range(1,1801):
        d=date(2026,8,1)+timedelta(days=rng.randrange(92));dk=int(d.strftime('%Y%m%d'));sk=rng.randint(1,6)
        for line,p in enumerate(rng.sample(PRODUCTS,rng.randint(1,3)),1):
            rows.append((f'E{i:05}',line,dk,p[0],sk,rng.randint(1,5),p[3]))
    make_db(targets[1],rows,True)
    if targets[2].exists():targets[2].unlink()
    with sqlite3.connect(targets[2]) as c:
        c.execute("CREATE TABLE orders(order_id TEXT PRIMARY KEY, status TEXT NOT NULL CHECK(status IN ('PENDING','PAID','CANCELLED')))")
        c.execute("INSERT INTO orders VALUES ('O1004','PENDING')")
    print(f'Created base: 8 lines / 6 orders. Extended: {len(rows)} lines / 1800 orders.')
if __name__=='__main__':main()
