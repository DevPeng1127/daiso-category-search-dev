"""Trace the exact pathfinding for 스포츠 zone"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.stdout.reconfigure(encoding="utf-8")

from app.data.store_locations import (
    B2_TABLET_PX, B2_START_NODE, B2_NODES_PX, B2_EDGES, B2_ZONES,
    _build_graph, _dijkstra, _normalize, _build_waypoints_floor,
    get_location, build_waypoints,
)

print("=== B2 스포츠 Zone 12 경로 추적 ===\n")

zone = B2_ZONES[12]
print(f"Zone: {zone}")
print(f"Start node: {B2_START_NODE} at {B2_NODES_PX[B2_START_NODE]}")
print(f"Target node: {zone['node']} at {B2_NODES_PX[zone['node']]}")
print(f"Zone dest: ({zone['x']}, {zone['y']})")
print(f"Tablet: {B2_TABLET_PX}")

graph = _build_graph(B2_NODES_PX, B2_EDGES)
print(f"\nNode 14 neighbors: {graph[14]}")
print(f"Node 15 neighbors: {graph[15]}")

node_path = _dijkstra(graph, B2_START_NODE, zone["node"])
print(f"\nDijkstra path: {node_path}")
print("Path coordinates:")
for nid in node_path:
    print(f"  Node {nid}: {B2_NODES_PX[nid]}")

print(f"\n=== Full waypoints (normalized) ===")
waypoints = build_waypoints(
    _normalize(zone["x"], zone["y"])[0],
    _normalize(zone["x"], zone["y"])[1],
    "B2", zone_id=12
)
for i, wp in enumerate(waypoints):
    px_x = int(wp["x"] * 863)
    px_y = int(wp["y"] * 1024)
    label = ["Tablet", *[f"Node {n}" for n in node_path], "Zone"][i]
    print(f"  [{i}] {label}: ({wp['x']:.4f}, {wp['y']:.4f}) = pixel ({px_x}, {px_y})")

# Also check via get_location for a 스포츠 product
print(f"\n=== 골프 퍼팅 연습 매트 경로 (via get_location) ===")
loc = get_location(
    category_middle="등산/수영/골프",
    category_major="스포츠/레저/취미",
    product_name="골프 퍼팅 연습 매트 2 m"
)
print(f"Location: floor={loc.floor}, zone_id={loc.zone_id}, x={loc.x:.4f}, y={loc.y:.4f}")
path = build_waypoints(loc.x, loc.y, loc.floor, zone_id=loc.zone_id)
print(f"Waypoints ({len(path)} points):")
for i, wp in enumerate(path):
    px_x = int(wp["x"] * 863)
    px_y = int(wp["y"] * 1024)
    print(f"  [{i}] ({wp['x']:.4f}, {wp['y']:.4f}) = pixel ({px_x}, {px_y})")

# Y direction check
print(f"\nY sequence (should be monotonically non-increasing for 'going up'):")
y_vals = [wp["y"] for wp in path]
print(f"  {y_vals}")
is_monotonic = all(y_vals[i] >= y_vals[i+1] for i in range(len(y_vals)-1))
print(f"  Monotonically non-increasing: {is_monotonic}")
if not is_monotonic:
    for i in range(len(y_vals)-1):
        if y_vals[i] < y_vals[i+1]:
            print(f"  *** DETOUR at step {i} -> {i+1}: y goes from {y_vals[i]:.4f} to {y_vals[i+1]:.4f} (DOWN then UP)")
