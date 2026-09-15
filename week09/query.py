"""Run a SELECT query file: python query.py data/warehouse.db queries.sql"""
import sys,sqlite3
from pathlib import Path
if len(sys.argv)!=3: raise SystemExit('Usage: python query.py DATABASE SQL_FILE')
p=Path(sys.argv[1]).resolve()
if not p.is_file(): raise SystemExit('Database not found. Check path or run lab.py.')
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as con:
    sql=Path(sys.argv[2]).read_text(encoding='utf-8')
    cur=con.execute(sql)
    print('\t'.join(x[0] for x in cur.description))
    for row in cur: print('\t'.join(map(str,row)))
