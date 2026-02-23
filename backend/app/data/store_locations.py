"""Store location data - middle category to physical store location mapping

Based on actual Daiso store floor plan:
- B1: 화장품, 시즌, 건강기능식품, 캐릭터, 문구, 패션, 파티·유아동,
      인테리어소품, 포장, 디지털, 식품
- B2: 스포츠, 반려동물, 수예, 캠핑/차량관리, 공구, 홈패브릭, 일본수입,
      욕실, 청소, 세탁, 득템, 수납, 내추럴코너, 주방, 원예, 여행
"""
import heapq
import math
from dataclasses import dataclass


@dataclass
class StoreLocation:
    counter_number: int
    floor: str
    section_description: str
    x: float
    y: float
    zone_id: int | None = None


# ===== Common =====

IMAGE_WIDTH = 863
IMAGE_HEIGHT = 1024


def _normalize(px_x: int, px_y: int) -> tuple[float, float]:
    """Convert pixel coordinates to normalized (0-1)"""
    return px_x / IMAGE_WIDTH, px_y / IMAGE_HEIGHT


def _euclidean_dist(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    """Euclidean distance between two pixel points"""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _build_graph(
    nodes: dict[int, tuple[int, int]], edges: list[tuple[int, int]]
) -> dict[int, list[tuple[int, float]]]:
    """Build adjacency list from nodes and edges"""
    graph: dict[int, list[tuple[int, float]]] = {i: [] for i in nodes}
    for a, b in edges:
        dist = _euclidean_dist(nodes[a], nodes[b])
        graph[a].append((b, dist))
        graph[b].append((a, dist))
    return graph


def _dijkstra(
    graph: dict[int, list[tuple[int, float]]], start_node: int, end_node: int
) -> list[int]:
    """Shortest path between two nodes using Dijkstra's algorithm."""
    if start_node == end_node:
        return [start_node]

    dist: dict[int, float] = {node: float("inf") for node in graph}
    prev: dict[int, int | None] = {node: None for node in graph}
    dist[start_node] = 0.0
    pq: list[tuple[float, int]] = [(0.0, start_node)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == end_node:
            break
        for v, w in graph[u]:
            new_dist = d + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))

    path: list[int] = []
    node: int | None = end_node
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path


# ===== B1 Graph Data =====

B1_TABLET_PX: tuple[int, int] = (415, 235)
B1_START_NODE = 1

B1_NODES_PX: dict[int, tuple[int, int]] = {
    1: (470, 235),
    2: (590, 235),
    3: (590, 285),
    4: (590, 475),
    5: (590, 575),
    6: (590, 590),
    7: (590, 700),
    8: (590, 780),
    9: (460, 780),
    10: (590, 925),
    11: (300, 780),
    12: (300, 830),
    13: (300, 900),
}

B1_EDGES: list[tuple[int, int]] = [
    (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),
    (6, 7), (7, 8), (8, 9), (8, 10),
    (9, 11), (11, 12), (12, 13),
]

B1_ZONES: dict[int, dict] = {
    1: {"name": "시즌", "x": 470, "y": 300, "node": 1},
    2: {"name": "건강기능식품", "x": 545, "y": 475, "node": 4},
    3: {"name": "캐릭터", "x": 530, "y": 590, "node": 6},
    4: {"name": "파티 유아동", "x": 520, "y": 700, "node": 7},
    5: {"name": "문구", "x": 300, "y": 700, "node": 11},
    6: {"name": "포장", "x": 150, "y": 780, "node": 11},
    7: {"name": "디지털", "x": 460, "y": 830, "node": 9},
    8: {"name": "식품", "x": 680, "y": 925, "node": 10},
    9: {"name": "인테리어 소품", "x": 640, "y": 780, "node": 8},
    10: {"name": "패션", "x": 725, "y": 575, "node": 5},
    11: {"name": "화장품", "x": 725, "y": 285, "node": 3},
}

_B1_GRAPH = _build_graph(B1_NODES_PX, B1_EDGES)


# ===== B2 Graph Data =====

B2_TABLET_PX: tuple[int, int] = (90, 965)
B2_START_NODE = 14

B2_NODES_PX: dict[int, tuple[int, int]] = {
    14: (120, 965),
    15: (120, 880),
    16: (240, 880),
    17: (240, 790),
    18: (345, 790),
    19: (360, 790),
    20: (465, 790),
    21: (530, 790),
    22: (575, 790),
    23: (575, 730),
    24: (575, 535),
    25: (575, 425),
    26: (575, 310),
    27: (575, 240),
    28: (465, 240),
    29: (605, 240),
    30: (685, 240),
    31: (760, 240),
}

B2_EDGES: list[tuple[int, int]] = [
    (14, 15), (15, 16), (16, 17),
    (17, 18), (18, 19), (19, 20), (20, 21), (21, 22),
    (22, 23), (23, 24), (24, 25), (25, 26), (26, 27),
    (27, 28), (27, 29), (29, 30), (30, 31),
]

B2_ZONES: dict[int, dict] = {
    12: {"name": "스포츠", "x": 120, "y": 770, "node": 15},
    13: {"name": "반려동물", "x": 240, "y": 745, "node": 17},
    14: {"name": "수예", "x": 345, "y": 745, "node": 18},
    15: {"name": "캠핑/차량관리", "x": 465, "y": 745, "node": 20},
    16: {"name": "공구", "x": 530, "y": 535, "node": 24},
    17: {"name": "홈패브릭", "x": 530, "y": 425, "node": 25},
    18: {"name": "일본수입", "x": 530, "y": 310, "node": 26},
    19: {"name": "욕실", "x": 465, "y": 180, "node": 28},
    20: {"name": "청소", "x": 605, "y": 180, "node": 29},
    21: {"name": "세탁", "x": 685, "y": 90, "node": 30},
    22: {"name": "득템", "x": 760, "y": 225, "node": 31},
    24: {"name": "수납", "x": 630, "y": 310, "node": 26},
    25: {"name": "내추럴코너", "x": 630, "y": 425, "node": 25},
    26: {"name": "주방", "x": 660, "y": 730, "node": 23},
    27: {"name": "원예", "x": 530, "y": 830, "node": 21},
    28: {"name": "여행", "x": 360, "y": 830, "node": 19},
}

_B2_GRAPH = _build_graph(B2_NODES_PX, B2_EDGES)


# ===== Waypoint builders =====

def _build_waypoints_floor(
    tablet_px: tuple[int, int],
    start_node: int,
    graph: dict[int, list[tuple[int, float]]],
    nodes_px: dict[int, tuple[int, int]],
    zones: dict[int, dict],
    zone_id: int,
) -> list[dict[str, float]]:
    """Build navigation waypoints using graph pathfinding.

    Path: Tablet -> start node -> [shortest path] -> zone's node -> zone
    """
    zone = zones[zone_id]
    target_node: int = zone["node"]
    node_path = _dijkstra(graph, start_node, target_node)

    points: list[dict[str, float]] = []

    # Start: Tablet position
    sx, sy = _normalize(*tablet_px)
    points.append({"x": sx, "y": sy})

    # Node waypoints
    for node_id in node_path:
        nx, ny = _normalize(*nodes_px[node_id])
        points.append({"x": nx, "y": ny})

    # End: Zone position
    zx, zy = _normalize(zone["x"], zone["y"])
    points.append({"x": zx, "y": zy})

    return points


# ===== Location helpers =====

def _b1_loc(zone_id: int) -> StoreLocation:
    """Create B1 StoreLocation from zone_id"""
    zone = B1_ZONES[zone_id]
    x, y = _normalize(zone["x"], zone["y"])
    return StoreLocation(zone_id, "B1", zone["name"], x, y, zone_id=zone_id)


def _b2_loc(zone_id: int) -> StoreLocation:
    """Create B2 StoreLocation from zone_id"""
    zone = B2_ZONES[zone_id]
    x, y = _normalize(zone["x"], zone["y"])
    return StoreLocation(zone_id, "B2", zone["name"], x, y, zone_id=zone_id)


# ===== Start positions =====

KIOSK_POSITION: dict[str, float] = {
    "x": B1_TABLET_PX[0] / IMAGE_WIDTH,
    "y": B1_TABLET_PX[1] / IMAGE_HEIGHT,
}


def get_start_position(floor: str) -> dict[str, float]:
    """Get start position for a floor"""
    if floor == "B2":
        return {
            "x": B2_TABLET_PX[0] / IMAGE_WIDTH,
            "y": B2_TABLET_PX[1] / IMAGE_HEIGHT,
        }
    return KIOSK_POSITION


# ===== Zone name -> StoreLocation =====

ZONE_LOCATIONS: dict[str, StoreLocation] = {
    # B1
    "시즌": _b1_loc(1),
    "건강기능식품": _b1_loc(2),
    "캐릭터": _b1_loc(3),
    "파티 유아동": _b1_loc(4),
    "문구": _b1_loc(5),
    "포장": _b1_loc(6),
    "디지털": _b1_loc(7),
    "식품": _b1_loc(8),
    "인테리어 소품": _b1_loc(9),
    "패션": _b1_loc(10),
    "화장품": _b1_loc(11),
    # B2
    "스포츠": _b2_loc(12),
    "반려동물": _b2_loc(13),
    "수예": _b2_loc(14),
    "캠핑/차량관리": _b2_loc(15),
    "공구": _b2_loc(16),
    "홈패브릭": _b2_loc(17),
    "일본수입": _b2_loc(18),
    "욕실": _b2_loc(19),
    "청소": _b2_loc(20),
    "세탁": _b2_loc(21),
    "득템": _b2_loc(22),
    "수납": _b2_loc(24),
    "내추럴코너": _b2_loc(25),
    "주방": _b2_loc(26),
    "원예": _b2_loc(27),
    "여행": _b2_loc(28),
}

# Keep for backward compatibility (tests etc.)
MIDDLE_CATEGORY_LOCATIONS = ZONE_LOCATIONS


# ===== (category_major, category_middle) -> zone name =====
# None as middle = default for that major

CATEGORY_TO_ZONE: dict[tuple[str, str | None], str] = {
    # 국민득템
    ("국민득템", None): "득템",

    # 뷰티/위생 → 화장품
    ("뷰티/위생", None): "화장품",

    # 주방용품 → 주방
    ("주방용품", None): "주방",

    # 청소/욕실 → 세부 분류
    ("청소/욕실", "욕실용품"): "욕실",
    ("청소/욕실", "수건/타월"): "욕실",
    ("청소/욕실", "탈취/제습제"): "욕실",
    ("청소/욕실", "세탁용품"): "세탁",
    ("청소/욕실", "세탁세제"): "세탁",
    ("청소/욕실", None): "청소",  # 청소용품, 주방/청소세제, 휴지통/비닐봉투

    # 수납/정리 → 수납
    ("수납/정리", None): "수납",

    # 문구/팬시 → 문구 (포장용품은 포장으로)
    ("문구/팬시", "포장용품"): "포장",
    ("문구/팬시", None): "문구",

    # 인테리어/원예 → 세부 분류
    ("인테리어/원예", "원예용품"): "원예",
    ("인테리어/원예", "조화"): "원예",
    ("인테리어/원예", "커튼용품"): "홈패브릭",
    ("인테리어/원예", "침구/쿠션/방석"): "홈패브릭",
    ("인테리어/원예", "방향제/캔들"): "내추럴코너",
    ("인테리어/원예", None): "인테리어 소품",

    # 공구/디지털 → 세부 분류
    ("공구/디지털", "공구용품"): "공구",
    ("공구/디지털", None): "디지털",  # 휴대폰, 컴퓨터, 건전지/콘센트 등

    # 식품 → 건강식품은 건강기능식품, 나머지 식품
    ("식품", "건강식품"): "건강기능식품",
    ("식품", None): "식품",

    # 스포츠/레저/취미 → 세부 분류
    ("스포츠/레저/취미", "수예용품"): "수예",
    ("스포츠/레저/취미", "자동차용품"): "캠핑/차량관리",
    ("스포츠/레저/취미", "홈트레이닝"): "스포츠",
    ("스포츠/레저/취미", "등산/수영/골프"): "스포츠",
    ("스포츠/레저/취미", "스포츠잡화"): "스포츠",
    ("스포츠/레저/취미", "취미/기호"): "수예",
    # 캠핑/여행은 상품명 키워드로 분기 (get_location에서 처리)
    ("스포츠/레저/취미", None): "스포츠",

    # 패션/잡화 → 패션
    ("패션/잡화", None): "패션",

    # 반려동물
    ("반려동물", None): "반려동물",

    # 유아/완구 → 인형은 캐릭터, 나머지 파티 유아동
    ("유아/완구", "인형"): "캐릭터",
    ("유아/완구", None): "파티 유아동",

    # 시즌/시리즈
    ("시즌/시리즈", None): "시즌",

    # 상품권
    ("상품권", None): "득템",
}

# Japanese import detection keywords
JAPANESE_KEYWORDS: list[str] = ["일본제"]


def get_location(
    category_middle: str | None = None,
    category_major: str | None = None,
    product_name: str | None = None,
) -> StoreLocation | None:
    """Get store location for a product.

    Priority:
    1. Japanese brand in product name -> 일본수입
    2. (category_major, category_middle) exact match
    3. (category_major, None) default for major
    4. Special: 캠핑/여행 split by product name keywords
    """
    # 1. Japanese brand override
    if product_name:
        for kw in JAPANESE_KEYWORDS:
            if kw in product_name:
                return ZONE_LOCATIONS["일본수입"]

    # 2. Exact (major, middle) match
    if category_major and category_middle:
        zone_name = CATEGORY_TO_ZONE.get((category_major, category_middle))
        if zone_name:
            return ZONE_LOCATIONS[zone_name]

    # 3. Special: 캠핑/여행 → split by keyword
    if category_middle == "캠핑/여행":
        if product_name and "여행" in product_name:
            return ZONE_LOCATIONS["여행"]
        return ZONE_LOCATIONS["캠핑/차량관리"]

    # 4. Default for major
    if category_major:
        zone_name = CATEGORY_TO_ZONE.get((category_major, None))
        if zone_name:
            return ZONE_LOCATIONS[zone_name]

    return None


def build_waypoints(
    dest_x: float, dest_y: float, floor: str = "B1", zone_id: int | None = None
) -> list[dict[str, float]]:
    """Build navigation waypoints from start to destination.

    Uses graph-based Dijkstra pathfinding through nodes for both B1 and B2.
    """
    if floor == "B1" and zone_id is not None:
        return _build_waypoints_floor(
            B1_TABLET_PX, B1_START_NODE, _B1_GRAPH, B1_NODES_PX, B1_ZONES, zone_id
        )

    if floor == "B2" and zone_id is not None:
        return _build_waypoints_floor(
            B2_TABLET_PX, B2_START_NODE, _B2_GRAPH, B2_NODES_PX, B2_ZONES, zone_id
        )

    # Fallback (no zone_id)
    start = get_start_position(floor)
    return [
        {"x": start["x"], "y": start["y"]},
        {"x": dest_x, "y": dest_y},
    ]
