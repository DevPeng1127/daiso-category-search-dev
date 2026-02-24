"""Inspect the clean DB category structure"""
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "database", "products.db")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== category_major → category_middle (with counts) ===")
cur.execute("""
    SELECT category_major, category_middle, COUNT(*) as cnt
    FROM products
    GROUP BY category_major, category_middle
    ORDER BY category_major, cnt DESC
""")
rows = cur.fetchall()
current = None
for r in rows:
    major, middle, cnt = r["category_major"], r["category_middle"], r["cnt"]
    if major != current:
        if current is not None:
            print()
        current = major
        print(f"[{major}]")
    print(f"  {cnt:4d}  {middle}")

print("\n\n=== Sample products per category_major ===")
cur.execute("SELECT DISTINCT category_major FROM products ORDER BY category_major")
majors = [r["category_major"] for r in cur.fetchall()]
for m in majors:
    cur.execute("SELECT id, name, category_middle FROM products WHERE category_major = ? LIMIT 3", (m,))
    print(f"\n[{m}]")
    for r in cur.fetchall():
        print(f"  [{r['id']:4d}] ({r['category_middle']}) {r['name']}")

# Check for Japanese brand products
print("\n\n=== Products with '일본제' in name ===")
cur.execute("SELECT id, name, category_major, category_middle FROM products WHERE name LIKE '%일본제%'")
for r in cur.fetchall():
    print(f"  [{r['id']:4d}] ({r['category_major']} > {r['category_middle']}) {r['name']}")

conn.close()
