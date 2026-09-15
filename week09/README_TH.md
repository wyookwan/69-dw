# เริ่มแลป OLTP OLAP และ Pivot
1. อ่าน Student_Lab.docx และเปิด Terminal ในโฟลเดอร์ student
2. สร้าง venv แล้วติดตั้ง `python -m pip install -r requirements.txt`
3. ข้อมูลพร้อมใช้ใน data/ ไม่ต้องดาวน์โหลดข้อมูลเพิ่ม
4. ทดลอง `python query.py data/warehouse.db queries.sql`
5. แก้ oltp_demo.py, queries.sql และ pivot_student.py ตามใบงาน
6. บันทึก SQL แต่ละข้อเป็น q01.sql ถึง q12.sql
7. เติมรายงานจาก Answer_Template.md และส่งตามใบงาน

lab.py สร้างข้อมูลด้วย seed 9033267; `python lab.py --reset` จะสร้างฐานและ CSV ที่ให้มาใหม่ ทิ้งการแก้ไขฐานทั้งสาม ให้สำรองงานก่อน
warehouse.db/warehouse.csv: ข้อมูลหลักตามสไลด์ 8 รายการ
extended.db/extended.csv: ชุดต่อยอด 3,649 รายการ
oltp.db: สถานะเริ่มต้น PENDING แยกจาก warehouse
ทุกจำนวนเงินเป็นบาท ไม่มีภาษี ส่วนลด คืนสินค้า ข้อมูลเป็นข้อมูลจำลองทั้งหมด
โปรแกรมใช้ pathlib จึงรองรับ Windows/macOS/Linux ใช้ python3 แทน python บน macOS ถ้าจำเป็น
หาก pandas หาย ให้ติดตั้ง requirements ด้วย Python ตัวเดียวกับที่ใช้รัน
หากเปิด CSV ใน Excel ต้องตั้ง amount เป็นตัวเลข และ Pivot เป็น Sum; บันทึกงาน Pivot เป็น .xlsx
