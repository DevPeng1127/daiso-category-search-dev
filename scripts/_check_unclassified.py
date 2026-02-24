"""Check for unclassified products"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.stdout.reconfigure(encoding="utf-8")

from app.data.store_locations import get_location, CATEGORY_TO_ZONE

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "backend", "database", "products.db"))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Check DB fields
print("=== DB에 미분류/NULL/빈값 카테고리 ===")
cur.execute("""
    SELECT COUNT(*) as cnt FROM products
    WHERE category_major IS NULL OR category_major = '' OR category_major = '미분류'
""")
print(f"  category_major 미분류: {cur.fetchone()['cnt']}개")

cur.execute("""
    SELECT COUNT(*) as cnt FROM products
    WHERE category_middle IS NULL OR category_middle = '' OR category_middle = '미분류'
""")
print(f"  category_middle 미분류: {cur.fetchone()['cnt']}개")

# 2. Golf products
print("\n=== 골프 관련 상품 ===")
cur.execute("SELECT id, name, category_major, category_middle FROM products WHERE name LIKE '%골프%'")
for r in cur.fetchall():
    loc = get_location(r["category_middle"], r["category_major"], r["name"])
    zone = loc.section_description if loc else "NONE"
    print(f"  [{r['id']:4d}] ({r['category_major']} > {r['category_middle']}) -> {zone}")
    print(f"         {r['name']}")

# 3. Check which (major, middle) pairs DON'T have exact match in CATEGORY_TO_ZONE
print("\n\n=== CATEGORY_TO_ZONE에 exact match 없이 fallback(default)으로 매핑되는 카테고리 ===")
cur.execute("""
    SELECT category_major, category_middle, COUNT(*) as cnt
    FROM products
    GROUP BY category_major, category_middle
    ORDER BY category_major, category_middle
""")
fallback_count = 0
fallback_products = 0
for r in cur.fetchall():
    major, middle = r["category_major"], r["category_middle"]
    # Check if exact match exists
    if (major, middle) in CATEGORY_TO_ZONE:
        continue
    # This pair falls back to (major, None) default
    loc = get_location(middle, major)
    zone = loc.section_description if loc else "NONE"
    fallback_count += 1
    fallback_products += r["cnt"]
    print(f"  {r['cnt']:4d}  ({major} > {middle}) -> {zone} (fallback)")

print(f"\n  총 {fallback_count}개 카테고리 조합, {fallback_products}개 상품이 fallback 매핑")

# 4. Check total
cur.execute("SELECT COUNT(*) as cnt FROM products")
total = cur.fetchone()["cnt"]
print(f"  전체 상품: {total}개")

conn.close()
