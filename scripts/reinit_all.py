"""Reinitialize all search indexes after DB update.

Usage: cd backend && poetry run python ../scripts/reinit_all.py
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


async def main() -> None:
    print("=" * 50)
    print("[DB Reinit] Step 1/3: Generating embeddings...")
    print("=" * 50)

    from database.embeddings import generate_embeddings
    generate_embeddings()

    print("\n" + "=" * 50)
    print("[DB Reinit] Step 2/3: Initializing Qdrant...")
    print("=" * 50)

    # Import and run init_qdrant logic
    from app.services.qdrant_service import QdrantService, deserialize_embedding
    from database.database import get_connection

    qdrant = QdrantService()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.price, p.image_url, e.text_embedding
        FROM products p
        JOIN product_embeddings e ON p.id = e.product_id
    """)
    rows = cursor.fetchall()
    print(f"  Found {len(rows)} products with embeddings")

    if rows:
        # Delete existing collection via HTTP API (avoids Windows file lock issues)
        import urllib.request
        from app.services.qdrant_service import COLLECTION_NAME
        from app.config import settings
        delete_url = f"{settings.QDRANT_URL}/collections/{COLLECTION_NAME}"
        try:
            req = urllib.request.Request(delete_url, method="DELETE")
            urllib.request.urlopen(req)
            print(f"  Deleted existing collection '{COLLECTION_NAME}'")
            await asyncio.sleep(1)  # wait for Qdrant to clean up
        except Exception:
            print(f"  No existing collection to delete (or already deleted)")
        await qdrant.recreate_collection()

        from qdrant_client.models import PointStruct
        points = []
        skipped = 0
        for row in rows:
            p_id, p_name, p_price, p_img, p_emb = row
            try:
                vector = deserialize_embedding(p_emb)
                if isinstance(vector, list) and len(vector) == 768:
                    points.append(PointStruct(
                        id=p_id, vector=vector,
                        payload={"name": p_name, "price": p_price, "image_url": p_img},
                    ))
                else:
                    skipped += 1
            except Exception:
                skipped += 1

        if points:
            uploaded = await qdrant.bulk_upsert(points)
            print(f"  [OK] Uploaded {uploaded} vectors (skipped: {skipped})")

    await qdrant.close()
    conn.close()

    print("\n" + "=" * 50)
    print("[DB Reinit] Step 3/3: Initializing Elasticsearch...")
    print("=" * 50)

    from database.database import get_all_products
    from database.category_matcher import init_category_tables, populate_categories, update_all_products
    from app.services.es_service import ESService

    init_category_tables()
    populate_categories()
    update_all_products()

    products = get_all_products()
    print(f"  Found {len(products)} products")

    es = ESService()
    await es.create_index()
    count = await es.bulk_index(products)
    es.close()

    print(f"  [OK] Indexed {count} products to Elasticsearch")

    print("\n" + "=" * 50)
    print("[DB Reinit] All done!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
