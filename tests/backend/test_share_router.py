"""Tests for share router"""
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_share_product_found(client):
    """Should return product and map info for valid product with location"""
    mock_product = {
        "id": 1,
        "rank": 1,
        "name": "대용량 물티슈",
        "price": 1000,
        "image_url": "/static/images/001.jpg",
        "category_major": "뷰티/위생",
        "category_middle": "화장지/물티슈",
    }

    with patch("app.routers.share.product_service") as mock_service:
        mock_service.get_product_by_id.return_value = mock_product
        response = client.get("/api/share/1")
        assert response.status_code == 200
        data = response.json()
        assert data["product"]["name"] == "대용량 물티슈"
        assert data["map_info"]["floor"] == "B1"
        assert data["map_info"]["waypoints"] is not None
        assert len(data["map_info"]["waypoints"]) > 0


def test_share_product_not_found(client):
    """Should return 404 for non-existent product"""
    with patch("app.routers.share.product_service") as mock_service:
        mock_service.get_product_by_id.return_value = None
        response = client.get("/api/share/9999")
        assert response.status_code == 404


def test_share_product_no_location(client):
    """Should return product with default map info if no location mapping"""
    mock_product = {
        "id": 100,
        "rank": 100,
        "name": "알 수 없는 상품",
        "price": 500,
        "image_url": "/static/images/100.jpg",
        "category_major": "기타",
        "category_middle": "알수없는카테고리",
    }

    with patch("app.routers.share.product_service") as mock_service:
        mock_service.get_product_by_id.return_value = mock_product
        response = client.get("/api/share/100")
        assert response.status_code == 200
        data = response.json()
        assert data["product"]["name"] == "알 수 없는 상품"
        assert data["map_info"]["floor"] == "B1"
