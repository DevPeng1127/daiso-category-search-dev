"""Check product-to-zone mapping accuracy"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.stdout.reconfigure(encoding="utf-8")

from app.data.store_locations import get_location

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "backend", "database", "products.db"))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== 베개 관련 ===")
cur.execute("SELECT id, name, category_major, category_middle FROM products WHERE name LIKE ?", ("%베개%",))
for r in cur.fetchall():
    loc = get_location(r["category_middle"], r["category_major"], r["name"])
    zone = loc.section_description if loc else "NONE"
    floor = loc.floor if loc else "?"
    print(f"  [{r['id']:4d}] {r['name']}")
    print(f"        DB: {r['category_major']} > {r['category_middle']}")
    print(f"        -> 매장위치: {floor} {zone}")

print("\n=== 귀마개 관련 ===")
cur.execute("SELECT id, name, category_major, category_middle FROM products WHERE name LIKE ?", ("%귀마개%",))
for r in cur.fetchall():
    loc = get_location(r["category_middle"], r["category_major"], r["name"])
    zone = loc.section_description if loc else "NONE"
    floor = loc.floor if loc else "?"
    print(f"  [{r['id']:4d}] {r['name']}")
    print(f"        DB: {r['category_major']} > {r['category_middle']}")
    print(f"        -> 매장위치: {floor} {zone}")

print("\n=== 매핑 결과 샘플 (major별 대표 상품) ===")
cur.execute("SELECT DISTINCT category_major FROM products ORDER BY category_major")
majors = [r["category_major"] for r in cur.fetchall()]
for m in majors:
    cur.execute(
        "SELECT id, name, category_major, category_middle FROM products WHERE category_major = ? LIMIT 3",
        (m,),
    )
    print(f"\n[{m}]")
    for r in cur.fetchall():
        loc = get_location(r["category_middle"], r["category_major"], r["name"])
        zone = loc.section_description if loc else "NONE"
        floor = loc.floor if loc else "?"
        nm = r["name"][:35]
        print(f"  {nm:<38s} ({r['category_middle']}) -> {floor} {zone}")

print("\n\n=== 전체 (major, middle) -> zone 매핑 현황 ===")
cur.execute("""
    SELECT category_major, category_middle, COUNT(*) as cnt
    FROM products
    GROUP BY category_major, category_middle
    ORDER BY category_major, category_middle
""")
for r in cur.fetchall():
    loc = get_location(r["category_middle"], r["category_major"])
    zone = loc.section_description if loc else "NONE"
    floor = loc.floor if loc else "?"
    print(f"  {r['cnt']:4d}  ({r['category_major']} > {r['category_middle']}) -> {floor} {zone}")

conn.close()
