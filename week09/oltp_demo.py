from pathlib import Path
import sqlite3
p=Path(__file__).resolve().parent/'data'/'oltp.db'
if not p.exists():raise SystemExit('Run lab.py first')
with sqlite3.connect(p) as con:
    print('Before:',con.execute('SELECT * FROM orders').fetchall())
    # TODO: replace pass with a guarded UPDATE using WHERE order_id and status.
    pass
    print('After:',con.execute('SELECT * FROM orders').fetchall())
# Run twice. Explain why the second guarded UPDATE should affect 0 rows.
