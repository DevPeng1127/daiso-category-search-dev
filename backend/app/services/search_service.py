"""Search service - hybrid search orchestration"""
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.models.schemas import SearchResponse, ProductResult, MapInfo, QueryInfo, Waypoint
from app.data.store_locations import get_location, build_waypoints, KIOSK_POSITION
from app.config import settings
from app.services.gemini_service import GeminiService
from app.services.es_service import ESService
from app.services.qdrant_service import QdrantService
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)

NOT_SEARCH_MESSAGE = "상품 위치 검색만 도와드릴 수 있어요. 찾으시는 상품명을 말씀해 주세요!"


class SearchService:
    """Hybrid search orchestration: Gemini intent → ES + Qdrant → Gemini rerank"""

    def __init__(self) -> None:
        self.gemini = GeminiService()
        self.es = ESService()
        self.qdrant = QdrantService()
        self.product_service = ProductService()

    async def search(self, query: str) -> SearchResponse:
        """Full search pipeline"""
        logger.info(f"[SEARCH] Received query: {query}")

        # Step 1-1: Classify intent
        intent = await self.gemini.classify_intent(query)
        logger.info(f"[SEARCH] Intent classification: {intent}")

        if intent == "not_search":
            logger.info(f"[SEARCH] Early return: not a product search query")
            return SearchResponse(
                results=[],
                map_info=None,
                query_info=QueryInfo(
                    original=query, intent="not_search", keywords=[]
                ),
                message=NOT_SEARCH_MESSAGE,
            )

        # Step 1-2: Extract keywords
        keywords = await self.gemini.extract_keywords(query)
        logger.info(f"[SEARCH] Extracted keywords: {keywords}")

        # Step 2: Parallel search - ES BM25 + Qdrant vector
        es_results, qdrant_results = await asyncio.gather(
            self._search_es(keywords),
            self._search_qdrant(keywords),
            return_exceptions=True,
        )

        if isinstance(es_results, Exception):
            logger.error(f"ES search error: {es_results}")
            es_results = []
        if isinstance(qdrant_results, Exception):
            logger.error(f"Qdrant search error: {qdrant_results}")
            qdrant_results = []

        logger.info(f"[SEARCH] ES results: {len(es_results)}, Qdrant results: {len(qdrant_results)}")

        # Step 3: Merge results (fusion method depends on config)
        if settings.FUSION_METHOD == "rrf":
            candidates = self._fuse_results(es_results, qdrant_results)
        else:
            candidates = self._weighted_fuse_results(es_results, qdrant_results)

        if not candidates:
            # Fallback to SQLite LIKE search
            candidates = self._fallback_search(keywords)
            logger.info(f"[SEARCH] Fallback SQLite results: {len(candidates)}")

        logger.info(f"[SEARCH] Total candidates after fusion: {len(candidates)}")

        # Step 4: Gemini reranking → Top 3
        if len(candidates) > 3:
            selected_ids = await self.gemini.rerank(query, keywords, candidates)
            top_results = self._order_by_ids(candidates, selected_ids)
        else:
            top_results = candidates[:3]

        # Step 4.5: Recommendation mode - fill to 3 if needed
        is_recommendation = False
        if len(top_results) < 3:
            is_recommendation = True
            top_results = self._fill_recommendations(top_results, keywords)

        logger.info(f"[SEARCH] Final results: {len(top_results)}, recommendation={is_recommendation}")

        # Build response
        product_results = []
        for i, p in enumerate(top_results):
            loc = get_location(p.get("category_middle"))
            product_results.append(
                ProductResult(
                    id=p.get("id", 0),
                    rank=i + 1,
                    name=p.get("name", ""),
                    price=p.get("price", 0),
                    image_url=f"/static/images/{p.get('image_name', '')}",
                    category_major=p.get("category_major"),
                    category_middle=p.get("category_middle"),
                    score=p.get("score", 0.0),
                    counter_number=loc.counter_number if loc else None,
                    destination_x=loc.x if loc else None,
                    destination_y=loc.y if loc else None,
                    location_floor=loc.floor if loc else None,
                    location_description=loc.section_description if loc else None,
                )
            )

        map_info = None
        if product_results:
            first = product_results[0]
            location = get_location(first.category_middle)
            if location:
                path = build_waypoints(location.x, location.y, location.floor)
                map_info = MapInfo(
                    floor=location.floor,
                    section=first.category_major or "",
                    map_image=f"/maps/map_{location.floor.lower()}.jpg",
                    counter_number=location.counter_number,
                    section_description=location.section_description,
                    destination=Waypoint(x=location.x, y=location.y),
                    start=Waypoint(x=KIOSK_POSITION["x"], y=KIOSK_POSITION["y"]),
                    waypoints=[Waypoint(x=p["x"], y=p["y"]) for p in path],
                )
            else:
                map_info = MapInfo(
                    section=first.category_major or "",
                )

        return SearchResponse(
            results=product_results,
            map_info=map_info,
            query_info=QueryInfo(
                original=query,
                intent=intent,
                keywords=keywords,
            ),
            message="찾으시는 상품과 비슷한 상품을 함께 노출합니다" if is_recommendation else None,
            is_recommendation=is_recommendation,
        )

    async def _search_es(self, keywords: list[str]) -> list[dict]:
        """Search via Elasticsearch BM25"""
        return await self.es.search(keywords)

    async def _search_qdrant(self, keywords: list[str]) -> list[dict]:
        """Search via Qdrant vector similarity"""
        try:
            from database.embeddings import get_text_embedding
            import pickle
            import numpy as np

            query_text = " ".join(keywords)
            embedding_bytes = get_text_embedding(query_text)
            embedding = pickle.loads(embedding_bytes)
            if isinstance(embedding, np.ndarray):
                vector = embedding.tolist()
            else:
                vector = list(embedding)
            return await self.qdrant.search(vector)
        except Exception as e:
            logger.error(f"Qdrant search prep failed: {e}")
            return []

    def _fuse_results(
        self, es_results: list[dict], qdrant_results: list[dict]
    ) -> list[dict]:
        """Reciprocal Rank Fusion (RRF) to merge ES and Qdrant results"""
        k = settings.RRF_K
        scores: dict[int, float] = {}
        product_map: dict[int, dict] = {}

        for rank, item in enumerate(es_results):
            pid = item["id"]
            scores[pid] = scores.get(pid, 0) + 1.0 / (k + rank + 1)
            product_map[pid] = item

        for rank, item in enumerate(qdrant_results):
            pid = item["id"]
            scores[pid] = scores.get(pid, 0) + 1.0 / (k + rank + 1)
            if pid not in product_map:
                product_map[pid] = item

        # Sort by RRF score descending
        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        result = []
        for pid in sorted_ids:
            p = product_map[pid]
            p["score"] = scores[pid]
            result.append(p)
        return result

    def _normalize_scores(self, results: list[dict]) -> list[dict]:
        """Min-max normalize scores to [0, 1] range"""
        if not results:
            return results
        scores = [r["score"] for r in results]
        min_s, max_s = min(scores), max(scores)
        rng = max_s - min_s
        for r in results:
            r["score"] = (r["score"] - min_s) / rng if rng > 0 else 1.0
        return results

    def _weighted_fuse_results(
        self, es_results: list[dict], qdrant_results: list[dict]
    ) -> list[dict]:
        """Weighted linear combination fusion of ES and Qdrant results"""
        bm25_boost = settings.BM25_BOOST
        vector_boost = settings.VECTOR_BOOST

        # Normalize scores independently
        es_norm = self._normalize_scores([{**r} for r in es_results])
        qd_norm = self._normalize_scores([{**r} for r in qdrant_results])

        scores: dict[int, float] = {}
        product_map: dict[int, dict] = {}

        for item in es_norm:
            pid = item["id"]
            scores[pid] = scores.get(pid, 0) + item["score"] * bm25_boost
            product_map[pid] = item

        for item in qd_norm:
            pid = item["id"]
            scores[pid] = scores.get(pid, 0) + item["score"] * vector_boost
            if pid not in product_map:
                product_map[pid] = item

        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        result = []
        for pid in sorted_ids:
            p = product_map[pid]
            p["score"] = scores[pid]
            result.append(p)
        return result

    def _fill_recommendations(
        self, results: list[dict], keywords: list[str]
    ) -> list[dict]:
        """Fill results up to 3 with similar products from SQLite"""
        if len(results) >= 3:
            return results[:3]
        existing_ids = {r["id"] for r in results}
        # 1차: 키워드 기반 보충
        for kw in keywords:
            for p in self.product_service.search_products(kw):
                if p["id"] not in existing_ids:
                    p["score"] = 0.0
                    results.append(p)
                    existing_ids.add(p["id"])
                if len(results) >= 3:
                    return results[:3]
        # 2차: 전체 상품에서 보충 (최종 폴백)
        if len(results) < 3:
            for p in self.product_service.get_all_products():
                if p["id"] not in existing_ids:
                    p["score"] = 0.0
                    results.append(p)
                    existing_ids.add(p["id"])
                if len(results) >= 3:
                    break
        return results[:3]

    def _fallback_search(self, keywords: list[str]) -> list[dict]:
        """Fallback to SQLite LIKE search"""
        all_results = []
        for kw in keywords:
            results = self.product_service.search_products(kw)
            all_results.extend(results)
        # Deduplicate
        seen = set()
        unique = []
        for r in all_results:
            if r["id"] not in seen:
                seen.add(r["id"])
                r["score"] = 0.5
                unique.append(r)
        return unique[:30]

    def _order_by_ids(
        self, candidates: list[dict], selected_ids: list[int]
    ) -> list[dict]:
        """Order candidates by selected IDs from reranking"""
        id_map = {c["id"]: c for c in candidates}
        result = []
        for pid in selected_ids:
            if pid in id_map:
                result.append(id_map[pid])
        # Fill up to 3 if reranking returned fewer
        if len(result) < 3:
            for c in candidates:
                if c["id"] not in {r["id"] for r in result}:
                    result.append(c)
                if len(result) >= 3:
                    break
        return result[:3]
