export interface Point {
  x: number;
  y: number;
}

// ===== Common =====

const IMAGE_WIDTH = 863;
const IMAGE_HEIGHT = 1024;

function normalize(pxX: number, pxY: number): Point {
  return { x: pxX / IMAGE_WIDTH, y: pxY / IMAGE_HEIGHT };
}

function euclideanDist(p1: [number, number], p2: [number, number]): number {
  return Math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2);
}

type AdjList = Record<number, { node: number; dist: number }[]>;

function buildGraph(
  nodes: Record<number, [number, number]>,
  edges: [number, number][],
): AdjList {
  const graph: AdjList = {};
  for (const id of Object.keys(nodes)) graph[Number(id)] = [];
  for (const [a, b] of edges) {
    const d = euclideanDist(nodes[a], nodes[b]);
    graph[a].push({ node: b, dist: d });
    graph[b].push({ node: a, dist: d });
  }
  return graph;
}

function dijkstra(graph: AdjList, startNode: number, endNode: number): number[] {
  if (startNode === endNode) return [startNode];

  const dist: Record<number, number> = {};
  const prev: Record<number, number | null> = {};
  for (const id of Object.keys(graph)) {
    const n = Number(id);
    dist[n] = Infinity;
    prev[n] = null;
  }
  dist[startNode] = 0;

  const pq: [number, number][] = [[0, startNode]];
  while (pq.length > 0) {
    pq.sort((a, b) => a[0] - b[0]);
    const [d, u] = pq.shift()!;
    if (d > dist[u]) continue;
    if (u === endNode) break;
    for (const { node: v, dist: w } of graph[u]) {
      const nd = d + w;
      if (nd < dist[v]) {
        dist[v] = nd;
        prev[v] = u;
        pq.push([nd, v]);
      }
    }
  }

  const path: number[] = [];
  let node: number | null = endNode;
  while (node !== null) {
    path.push(node);
    node = prev[node];
  }
  path.reverse();
  return path;
}

function buildWaypointsFloor(
  tabletPx: [number, number],
  startNode: number,
  graph: AdjList,
  nodesPx: Record<number, [number, number]>,
  zones: Record<number, { x: number; y: number; node: number }>,
  zoneId: number,
): Point[] {
  const zone = zones[zoneId];
  const nodePath = dijkstra(graph, startNode, zone.node);

  const points: Point[] = [];
  points.push(normalize(...tabletPx));
  for (const nid of nodePath) points.push(normalize(...nodesPx[nid]));
  points.push(normalize(zone.x, zone.y));
  return points;
}

// ===== B1 Graph Data =====

const B1_TABLET_PX: [number, number] = [415, 235];
const B1_START_NODE = 1;

const B1_NODES_PX: Record<number, [number, number]> = {
  1: [470, 235], 2: [590, 235], 3: [590, 285],
  4: [590, 475], 5: [590, 575], 6: [590, 590],
  7: [590, 700], 8: [590, 780], 9: [460, 780],
  10: [590, 925], 11: [300, 780], 12: [300, 830], 13: [300, 900],
};

const B1_EDGES: [number, number][] = [
  [1, 2], [2, 3], [3, 4], [4, 5], [5, 6],
  [6, 7], [7, 8], [8, 9], [8, 10],
  [9, 11], [11, 12], [12, 13],
];

export interface Zone {
  name: string;
  x: number;
  y: number;
  node: number;
}

export const B1_ZONES: Record<number, Zone> = {
  1: { name: '시즌', x: 470, y: 300, node: 1 },
  2: { name: '건강기능식품', x: 545, y: 475, node: 4 },
  3: { name: '캐릭터', x: 530, y: 590, node: 6 },
  4: { name: '파티/유아동', x: 520, y: 700, node: 7 },
  5: { name: '문구', x: 300, y: 700, node: 11 },
  6: { name: '포장', x: 150, y: 780, node: 11 },
  7: { name: '디지털', x: 460, y: 830, node: 9 },
  8: { name: '식품', x: 680, y: 925, node: 10 },
  9: { name: '인테리어소품', x: 640, y: 780, node: 8 },
  10: { name: '패션', x: 725, y: 575, node: 5 },
  11: { name: '화장품', x: 725, y: 285, node: 3 },
};

const B1_GRAPH = buildGraph(B1_NODES_PX, B1_EDGES);

// ===== B2 Graph Data =====

const B2_TABLET_PX: [number, number] = [90, 965];
const B2_START_NODE = 14;

const B2_NODES_PX: Record<number, [number, number]> = {
  14: [120, 965], 15: [120, 880], 16: [240, 880],
  17: [240, 790], 18: [345, 790], 19: [360, 790],
  20: [465, 790], 21: [530, 790], 22: [575, 790],
  23: [575, 730], 24: [575, 535], 25: [575, 425],
  26: [575, 310], 27: [575, 240], 28: [465, 240],
  29: [605, 240], 30: [685, 240], 31: [760, 240],
};

const B2_EDGES: [number, number][] = [
  [14, 15], [15, 16], [16, 17],
  [17, 18], [18, 19], [19, 20], [20, 21], [21, 22],
  [22, 23], [23, 24], [24, 25], [25, 26], [26, 27],
  [27, 28], [27, 29], [29, 30], [30, 31],
];

export const B2_ZONES: Record<number, Zone> = {
  12: { name: '스포츠', x: 120, y: 770, node: 15 },
  13: { name: '반려동물', x: 240, y: 745, node: 17 },
  14: { name: '수예', x: 345, y: 745, node: 18 },
  15: { name: '캠핑/차량관리', x: 465, y: 745, node: 20 },
  16: { name: '공구', x: 530, y: 535, node: 24 },
  17: { name: '홈패브릭', x: 530, y: 425, node: 25 },
  18: { name: '일본수입', x: 530, y: 310, node: 26 },
  19: { name: '욕실', x: 465, y: 180, node: 28 },
  20: { name: '청소', x: 605, y: 180, node: 29 },
  21: { name: '세탁', x: 685, y: 90, node: 30 },
  22: { name: '득템', x: 760, y: 225, node: 31 },
  24: { name: '수납', x: 630, y: 310, node: 26 },
  25: { name: '내추럴코너', x: 630, y: 425, node: 25 },
  26: { name: '주방', x: 660, y: 730, node: 23 },
  27: { name: '원예', x: 530, y: 830, node: 21 },
  28: { name: '여행', x: 360, y: 830, node: 19 },
};

const B2_GRAPH = buildGraph(B2_NODES_PX, B2_EDGES);

// ===== Exports =====

export const KIOSK_POSITION: Point = normalize(...B1_TABLET_PX);

export function getStartPosition(floor?: string): Point {
  if (floor === 'B2') return normalize(...B2_TABLET_PX);
  return KIOSK_POSITION;
}

/**
 * Build navigation waypoints from start to destination.
 * Uses graph-based Dijkstra pathfinding for both B1 and B2.
 */
export function buildWaypoints(
  destX: number,
  destY: number,
  floor?: string,
  zoneId?: number,
): Point[] {
  if (floor === 'B1' && zoneId != null) {
    return buildWaypointsFloor(
      B1_TABLET_PX, B1_START_NODE, B1_GRAPH, B1_NODES_PX, B1_ZONES, zoneId,
    );
  }

  if (floor === 'B2' && zoneId != null) {
    return buildWaypointsFloor(
      B2_TABLET_PX, B2_START_NODE, B2_GRAPH, B2_NODES_PX, B2_ZONES, zoneId,
    );
  }

  // Fallback (no zoneId) - use floor-specific start position
  const start = getStartPosition(floor);
  return [
    { x: start.x, y: start.y },
    { x: destX, y: destY },
  ];
}
