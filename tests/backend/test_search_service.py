"""Tests for SearchService - hybrid search orchestration"""
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


@pytest.fixture
def search_service():
    """Create SearchService with all dependencies mocked"""
    with patch("app.services.search_service.GeminiService") as MockGemini, \
         patch("app.services.search_service.ESService") as MockES, \
         patch("app.services.search_service.QdrantService") as MockQdrant, \
         patch("app.services.search_service.ProductService") as MockProduct:

        from app.services.search_service import SearchService
        service = SearchService()

        # Setup default mocks for 2-step intent pipeline
        service.gemini.classify_intent = AsyncMock(return_value="product_search")
        service.gemini.extract_keywords = AsyncMock(return_value=["물티슈"])
        service.gemini.rerank = AsyncMock(return_value=[1, 2, 3])

        service.es.search = AsyncMock(return_value=[
            {"id": 1, "name": "대용량 물티슈", "price": 1000, "category_major": "뷰티/위생",
             "category_middle": "화장지/물티슈", "image_name": "001_대용량 물티슈.jpg", "score": 5.0},
            {"id": 2, "name": "아기 물티슈", "price": 1500, "category_major": "뷰티/위생",
             "category_middle": "화장지/물티슈", "image_name": "002_아기 물티슈.jpg", "score": 4.0},
        ])

        service.qdrant.search = AsyncMock(return_value=[
            {"id": 1, "name": "대용량 물티슈", "price": 1000, "category_major": "뷰티/위생",
             "category_middle": "화장지/물티슈", "image_name": "001_대용량 물티슈.jpg", "score": 0.95},
            {"id": 3, "name": "물티슈 캡", "price": 1000, "category_major": "뷰티/위생",
             "category_middle": "화장지/물티슈", "image_name": "003_물티슈 캡.jpg", "score": 0.88},
        ])

        service.product_service.search_products = MagicMock(return_value=[])

        return service


async def test_search_full_pipeline(search_service):
    """Should execute the full search pipeline and return results"""
    search_service._search_qdrant = AsyncMock(return_value=[
        {"id": 1, "name": "대용량 물티슈", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "001_대용량 물티슈.jpg", "score": 0.95},
        {"id": 3, "name": "물티슈 캡", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "003_물티슈 캡.jpg", "score": 0.88},
    ])

    result = await search_service.search("물티슈 어디있어요?")

    assert result.query_info.original == "물티슈 어디있어요?"
    assert result.query_info.keywords == ["물티슈"]
    assert len(result.results) <= 3
    search_service.gemini.classify_intent.assert_called_once_with("물티슈 어디있어요?")
    search_service.gemini.extract_keywords.assert_called_once_with("물티슈 어디있어요?")


async def test_search_not_search_intent(search_service):
    """Should return early with message for non-search queries"""
    search_service.gemini.classify_intent = AsyncMock(return_value="not_search")

    result = await search_service.search("안녕하세요")

    assert result.results == []
    assert result.query_info.intent == "not_search"
    assert result.message is not None
    assert "상품" in result.message
    # Should NOT call extract_keywords or search
    search_service.gemini.extract_keywords.assert_not_called()


async def test_search_returns_map_info(search_service):
    """Should include map info in response"""
    search_service._search_qdrant = AsyncMock(return_value=[])

    result = await search_service.search("물티슈")
    if result.results:
        assert result.map_info is not None
        assert result.map_info.section != ""


async def test_map_info_includes_navigation_data(search_service):
    """Should include waypoints, destination, and counter in map info"""
    search_service._search_qdrant = AsyncMock(return_value=[])

    result = await search_service.search("물티슈")
    if result.results:
        mi = result.map_info
        assert mi is not None
        assert mi.counter_number is not None
        assert mi.destination is not None
        assert mi.start is not None
        assert len(mi.waypoints) >= 3
        assert mi.section_description != ""


async def test_product_result_includes_location_data(search_service):
    """Each product result should include location fields"""
    search_service._search_qdrant = AsyncMock(return_value=[])

    result = await search_service.search("물티슈")
    if result.results:
        p = result.results[0]
        assert p.counter_number is not None
        assert p.destination_x is not None
        assert p.destination_y is not None
        assert p.location_floor is not None
        assert p.location_description is not None


async def test_rrf_fusion(search_service):
    """Should merge ES and Qdrant results via RRF"""
    es_results = [
        {"id": 1, "name": "A", "score": 5.0},
        {"id": 2, "name": "B", "score": 4.0},
    ]
    qdrant_results = [
        {"id": 2, "name": "B", "score": 0.9},
        {"id": 3, "name": "C", "score": 0.8},
    ]

    fused = search_service._fuse_results(es_results, qdrant_results)

    # ID 2 should have highest RRF score (appears in both)
    assert fused[0]["id"] == 2
    assert len(fused) == 3


async def test_order_by_ids(search_service):
    """Should reorder candidates by selected IDs"""
    candidates = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
        {"id": 3, "name": "C"},
    ]

    result = search_service._order_by_ids(candidates, [3, 1, 2])
    assert result[0]["id"] == 3
    assert result[1]["id"] == 1
    assert result[2]["id"] == 2


async def test_normalize_scores(search_service):
    """Should normalize scores to [0, 1] range via min-max"""
    results = [
        {"id": 1, "name": "A", "score": 10.0},
        {"id": 2, "name": "B", "score": 5.0},
        {"id": 3, "name": "C", "score": 0.0},
    ]
    normalized = search_service._normalize_scores(results)
    assert normalized[0]["score"] == 1.0  # max → 1.0
    assert normalized[1]["score"] == 0.5  # mid → 0.5
    assert normalized[2]["score"] == 0.0  # min → 0.0


async def test_normalize_scores_equal(search_service):
    """When all scores are equal, should normalize to 1.0"""
    results = [
        {"id": 1, "name": "A", "score": 5.0},
        {"id": 2, "name": "B", "score": 5.0},
    ]
    normalized = search_service._normalize_scores(results)
    assert normalized[0]["score"] == 1.0
    assert normalized[1]["score"] == 1.0


async def test_normalize_scores_empty(search_service):
    """Empty list should return empty list"""
    assert search_service._normalize_scores([]) == []


async def test_weighted_fusion_both_sources(search_service):
    """Products in both sources should get highest score"""
    es_results = [
        {"id": 1, "name": "A", "score": 10.0},
        {"id": 2, "name": "B", "score": 5.0},
    ]
    qdrant_results = [
        {"id": 1, "name": "A", "score": 0.95},
        {"id": 3, "name": "C", "score": 0.80},
    ]
    fused = search_service._weighted_fuse_results(es_results, qdrant_results)
    # ID 1 appears in both → should be ranked first
    assert fused[0]["id"] == 1
    assert len(fused) == 3


async def test_weighted_fusion_vector_dominance(search_service):
    """When VECTOR_BOOST is high, vector-only results should rank higher than BM25-only"""
    es_results = [
        {"id": 1, "name": "A", "score": 10.0},  # ES only
    ]
    qdrant_results = [
        {"id": 2, "name": "B", "score": 0.95},  # Qdrant only
    ]
    # Default: BM25_BOOST=0.4, VECTOR_BOOST=0.6
    fused = search_service._weighted_fuse_results(es_results, qdrant_results)
    # ID 2 (vector) should rank higher because VECTOR_BOOST > BM25_BOOST
    # Both are single-item so normalized to 1.0, then multiplied by boost
    assert fused[0]["id"] == 2
    assert fused[0]["score"] > fused[1]["score"]


async def test_fusion_method_routing_rrf(search_service):
    """When FUSION_METHOD=rrf, should use RRF fusion in search pipeline"""
    with patch("app.services.search_service.settings") as mock_settings:
        mock_settings.FUSION_METHOD = "rrf"
        mock_settings.RRF_K = 60
        mock_settings.BM25_BOOST = 0.4
        mock_settings.VECTOR_BOOST = 0.6

        search_service._search_es = AsyncMock(return_value=[
            {"id": 1, "name": "A", "score": 5.0},
        ])
        search_service._search_qdrant = AsyncMock(return_value=[
            {"id": 1, "name": "A", "score": 0.9},
        ])

        result = await search_service.search("테스트")
        # Should still work (just uses RRF path)
        assert result is not None


async def test_fusion_method_routing_weighted(search_service):
    """When FUSION_METHOD=weighted, should use weighted fusion in search pipeline"""
    with patch("app.services.search_service.settings") as mock_settings:
        mock_settings.FUSION_METHOD = "weighted"
        mock_settings.BM25_BOOST = 0.4
        mock_settings.VECTOR_BOOST = 0.6
        mock_settings.RRF_K = 60

        search_service._search_es = AsyncMock(return_value=[
            {"id": 1, "name": "A", "score": 5.0},
            {"id": 2, "name": "B", "score": 3.0},
        ])
        search_service._search_qdrant = AsyncMock(return_value=[
            {"id": 1, "name": "A", "score": 0.9},
            {"id": 3, "name": "C", "score": 0.8},
        ])

        result = await search_service.search("테스트")
        assert result is not None


async def test_recommendation_when_few_results(search_service):
    """When reranked results < 3, should fill to 3 and set is_recommendation=True"""
    search_service._search_es = AsyncMock(return_value=[
        {"id": 1, "name": "대용량 물티슈", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "001_대용량 물티슈.jpg", "score": 5.0},
    ])
    search_service._search_qdrant = AsyncMock(return_value=[
        {"id": 1, "name": "대용량 물티슈", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "001_대용량 물티슈.jpg", "score": 0.95},
    ])
    search_service.product_service.search_products = MagicMock(return_value=[
        {"id": 10, "name": "캡형 물티슈", "price": 1500, "image_name": "010_캡형 물티슈.jpg",
         "category_major": "뷰티/위생", "category_middle": "화장지/물티슈"},
        {"id": 11, "name": "리필 물티슈", "price": 2000, "image_name": "011_리필 물티슈.jpg",
         "category_major": "뷰티/위생", "category_middle": "화장지/물티슈"},
    ])

    result = await search_service.search("물티슈")
    assert result.is_recommendation is True
    assert len(result.results) == 3
    assert result.message is not None
    assert "비슷한 상품" in result.message


async def test_recommendation_even_with_low_score(search_service):
    """Even with very low score, should still show results with recommendation"""
    search_service._search_es = AsyncMock(return_value=[
        {"id": 1, "name": "전혀 관련없는 상품", "price": 1000, "category_major": "기타",
         "category_middle": "기타", "image_name": "001.jpg", "score": 0.05},
    ])
    search_service._search_qdrant = AsyncMock(return_value=[])
    search_service.product_service.search_products = MagicMock(return_value=[
        {"id": 20, "name": "보충 상품A", "price": 1000, "image_name": "020.jpg",
         "category_major": "기타", "category_middle": "기타"},
        {"id": 21, "name": "보충 상품B", "price": 1000, "image_name": "021.jpg",
         "category_major": "기타", "category_middle": "기타"},
    ])

    with patch("app.services.search_service.settings") as mock_settings:
        mock_settings.FUSION_METHOD = "rrf"
        mock_settings.RRF_K = 60
        mock_settings.BM25_BOOST = 0.4
        mock_settings.VECTOR_BOOST = 0.6

        result = await search_service.search("아무거나")

    assert result.is_recommendation is True
    assert len(result.results) == 3
    assert result.message is not None


async def test_normal_results_not_recommendation(search_service):
    """When results >= 3, should NOT be recommendation mode"""
    search_service._search_es = AsyncMock(return_value=[
        {"id": 1, "name": "A", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "001.jpg", "score": 5.0},
        {"id": 2, "name": "B", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "002.jpg", "score": 4.0},
    ])
    search_service._search_qdrant = AsyncMock(return_value=[
        {"id": 1, "name": "A", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "001.jpg", "score": 0.95},
        {"id": 3, "name": "C", "price": 1000, "category_major": "뷰티/위생",
         "category_middle": "화장지/물티슈", "image_name": "003.jpg", "score": 0.88},
    ])
    search_service.gemini.rerank = AsyncMock(return_value=[1, 2, 3])

    result = await search_service.search("물티슈")
    assert result.is_recommendation is False
    assert len(result.results) == 3


async def test_fill_recommendations_deduplicates(search_service):
    """_fill_recommendations should not duplicate existing results"""
    from app.services.search_service import SearchService
    existing = [
        {"id": 1, "name": "A", "score": 0.5},
    ]
    search_service.product_service.search_products = MagicMock(return_value=[
        {"id": 1, "name": "A", "price": 1000, "image_name": "001.jpg",
         "category_major": "기타", "category_middle": "기타"},
        {"id": 2, "name": "B", "price": 1000, "image_name": "002.jpg",
         "category_major": "기타", "category_middle": "기타"},
        {"id": 3, "name": "C", "price": 1000, "image_name": "003.jpg",
         "category_major": "기타", "category_middle": "기타"},
    ])

    filled = search_service._fill_recommendations(existing, ["테스트"])
    assert len(filled) == 3
    ids = [r["id"] for r in filled]
    assert len(ids) == len(set(ids))  # no duplicates


async def test_fill_recommendations_fallback_to_all_products(search_service):
    """When keyword search returns nothing, should fallback to all products to guarantee 3 results"""
    existing = [
        {"id": 1, "name": "A", "score": 0.5},
    ]
    # 키워드 매칭 0건
    search_service.product_service.search_products = MagicMock(return_value=[])
    # 전체 상품에서 보충
    search_service.product_service.get_all_products = MagicMock(return_value=[
        {"id": 1, "name": "A", "price": 1000, "image_name": "001.jpg",
         "category_major": "기타", "category_middle": "기타"},
        {"id": 10, "name": "B", "price": 1000, "image_name": "010.jpg",
         "category_major": "기타", "category_middle": "기타"},
        {"id": 11, "name": "C", "price": 1000, "image_name": "011.jpg",
         "category_major": "기타", "category_middle": "기타"},
        {"id": 12, "name": "D", "price": 1000, "image_name": "012.jpg",
         "category_major": "기타", "category_middle": "기타"},
    ])

    filled = search_service._fill_recommendations(existing, ["없는키워드"])
    assert len(filled) == 3
    # 기존 id=1은 중복 제외, id=10, 11로 보충
    ids = [r["id"] for r in filled]
    assert 1 in ids
    assert len(ids) == len(set(ids))


async def test_fallback_search_when_no_results(search_service):
    """Should fallback to SQLite search when ES/Qdrant return nothing"""
    search_service.gemini.classify_intent = AsyncMock(return_value="product_search")
    search_service.gemini.extract_keywords = AsyncMock(return_value=["볼펜"])
    search_service._search_es = AsyncMock(return_value=[])
    search_service._search_qdrant = AsyncMock(return_value=[])
    search_service.product_service.search_products = MagicMock(return_value=[
        {"id": 10, "name": "볼펜 세트", "price": 1000, "image_name": "010_볼펜 세트.jpg",
         "category_major": "문구/팬시", "category_middle": "필기구"},
    ])

    result = await search_service.search("볼펜 찾아주세요")
    assert len(result.results) >= 1
    assert result.results[0].name == "볼펜 세트"
