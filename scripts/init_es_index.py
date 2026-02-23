"""Initialize Elasticsearch index with product data from SQLite"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database.database import get_all_products
from app.services.es_service import ESService


async def main() -> None:
    print("=" * 50)
    print("[ES Index Initialization]")
    print("=" * 50)

    # NOTE: Do NOT call category_matcher.update_all_products() here.
    # SQLite already has correct categories from reclassify_products.py.
    # Re-running the keyword matcher would overwrite them with "미분류".

    # Step 1: Get all products
    products = get_all_products()
    print(f"\n[1/2] Found {len(products)} products in SQLite")

    # Step 2: Index to Elasticsearch
    print("\n[2/2] Indexing to Elasticsearch...")
    es = ESService()
    await es.create_index()
    count = await es.bulk_index(products)
    es.close()

    print(f"\n[OK] Indexed {count} products to Elasticsearch")


if __name__ == "__main__":
    asyncio.run(main())
