"""Tests for store_locations - middle category to store location mapping"""
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.data.store_locations import (
    StoreLocation,
    MIDDLE_CATEGORY_LOCATIONS,
    KIOSK_POSITION,
    get_location,
    build_waypoints,
)


def test_store_location_dataclass():
    """StoreLocation should hold counter_number, floor, description, x, y"""
    loc = StoreLocation(
        counter_number=1, floor="B1", section_description="화장품 코너", x=0.82, y=0.18
    )
    assert loc.counter_number == 1
    assert loc.floor == "B1"
    assert loc.section_description == "화장품 코너"
    assert loc.x == 0.82
    assert loc.y == 0.18


def test_middle_category_locations_has_entries():
    """Should have mappings for all middle categories"""
    assert len(MIDDLE_CATEGORY_LOCATIONS) >= 27
    for key, loc in MIDDLE_CATEGORY_LOCATIONS.items():
        assert isinstance(loc, StoreLocation)
        assert 0.0 <= loc.x <= 1.0
        assert 0.0 <= loc.y <= 1.0
        assert loc.counter_number >= 1


def test_floors_are_b1_or_b2():
    """All locations should be on B1 or B2"""
    for key, loc in MIDDLE_CATEGORY_LOCATIONS.items():
        assert loc.floor in ("B1", "B2"), f"{key} has invalid floor {loc.floor}"


def test_kiosk_position():
    """Kiosk position should be near top area (B1 entrance)"""
    assert "x" in KIOSK_POSITION
    assert "y" in KIOSK_POSITION
    assert KIOSK_POSITION["y"] < 0.3  # upper area of map


def test_get_location_known_category():
    """Should return StoreLocation for known middle category"""
    loc = get_location(category_middle="스킨케어", category_major="뷰티/위생")
    assert loc is not None
    assert isinstance(loc, StoreLocation)
    assert loc.floor == "B1"

    loc2 = get_location(category_middle="욕실용품", category_major="청소/욕실")
    assert loc2 is not None
    assert loc2.floor == "B2"


def test_get_location_unknown_category():
    """Should return None for unknown category"""
    assert get_location("존재하지않는카테고리") is None
    assert get_location(None) is None


def test_build_waypoints_b1():
    """Should return graph path from kiosk to B1 zone"""
    loc = get_location(category_middle="스킨케어", category_major="뷰티/위생")  # zone 11
    assert loc is not None
    path = build_waypoints(loc.x, loc.y, "B1", zone_id=loc.zone_id)
    assert len(path) >= 3
    # First point should be kiosk position
    assert path[0]["x"] == KIOSK_POSITION["x"]
    assert path[0]["y"] == KIOSK_POSITION["y"]
    # Last point should be zone destination
    assert abs(path[-1]["x"] - loc.x) < 0.01
    assert abs(path[-1]["y"] - loc.y) < 0.01


def test_build_waypoints_b2():
    """Should return graph path for B2 zone"""
    from app.data.store_locations import get_start_position
    loc = get_location(category_middle="주방잡화", category_major="주방용품")  # zone 26
    assert loc is not None
    start = get_start_position("B2")
    path = build_waypoints(loc.x, loc.y, "B2", zone_id=loc.zone_id)
    assert len(path) >= 3
    assert path[0]["x"] == start["x"]
    assert path[0]["y"] == start["y"]


def test_build_waypoints_fallback_without_zone_id():
    """Without zone_id, should return direct 2-point path"""
    path = build_waypoints(0.5, 0.5, "B1")
    assert len(path) == 2
    assert path[0]["x"] == KIOSK_POSITION["x"]
    assert path[-1]["x"] == 0.5


def test_build_waypoints_all_coords_normalized():
    """All waypoint coordinates should be between 0.0 and 1.0"""
    path = build_waypoints(0.82, 0.72, "B2")
    for point in path:
        assert 0.0 <= point["x"] <= 1.0
        assert 0.0 <= point["y"] <= 1.0
