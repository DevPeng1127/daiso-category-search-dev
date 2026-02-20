import { describe, it, expect } from 'vitest';
import { buildWaypoints, KIOSK_POSITION } from '../../utils/pathfinding';

describe('pathfinding', () => {
  it('should export KIOSK_POSITION from Tablet 1 (normalized)', () => {
    expect(KIOSK_POSITION.x).toBeCloseTo(415 / 863, 4);
    expect(KIOSK_POSITION.y).toBeCloseTo(235 / 1024, 4);
  });

  describe('B1 graph-based routing', () => {
    it('should build path to Zone 11 (화장품) via nodes 1->2->3', () => {
      const path = buildWaypoints(0, 0, 'B1', 11);
      expect(path.length).toBe(5);
      expect(path[0].x).toBeCloseTo(415 / 863, 4);
      expect(path[0].y).toBeCloseTo(235 / 1024, 4);
      expect(path[path.length - 1].x).toBeCloseTo(725 / 863, 4);
      expect(path[path.length - 1].y).toBeCloseTo(285 / 1024, 4);
    });

    it('should build path to Zone 1 (시즌) via node 1 only', () => {
      const path = buildWaypoints(0, 0, 'B1', 1);
      expect(path.length).toBe(3);
      expect(path[path.length - 1].x).toBeCloseTo(470 / 863, 4);
      expect(path[path.length - 1].y).toBeCloseTo(300 / 1024, 4);
    });

    it('should have all B1 coordinates normalized 0~1', () => {
      for (let zoneId = 1; zoneId <= 11; zoneId++) {
        const path = buildWaypoints(0, 0, 'B1', zoneId);
        for (const p of path) {
          expect(p.x).toBeGreaterThanOrEqual(0);
          expect(p.x).toBeLessThanOrEqual(1);
          expect(p.y).toBeGreaterThanOrEqual(0);
          expect(p.y).toBeLessThanOrEqual(1);
        }
      }
    });
  });

  describe('B2 graph-based routing', () => {
    it('should start from Tablet 3 position', () => {
      const path = buildWaypoints(0, 0, 'B2', 19);
      expect(path[0].x).toBeCloseTo(90 / 863, 4);
      expect(path[0].y).toBeCloseTo(965 / 1024, 4);
    });

    it('should build path to Zone 19 (욕실)', () => {
      const path = buildWaypoints(0, 0, 'B2', 19);
      expect(path.length).toBeGreaterThan(3);
      expect(path[path.length - 1].x).toBeCloseTo(465 / 863, 4);
      expect(path[path.length - 1].y).toBeCloseTo(180 / 1024, 4);
    });

    it('should build path to Zone 26 (주방)', () => {
      const path = buildWaypoints(0, 0, 'B2', 26);
      expect(path[path.length - 1].x).toBeCloseTo(660 / 863, 4);
      expect(path[path.length - 1].y).toBeCloseTo(730 / 1024, 4);
    });

    it('should build path to Zone 13 (반려동물)', () => {
      const path = buildWaypoints(0, 0, 'B2', 13);
      expect(path[path.length - 1].x).toBeCloseTo(240 / 863, 4);
      expect(path[path.length - 1].y).toBeCloseTo(745 / 1024, 4);
    });

    it('should have all B2 coordinates normalized 0~1', () => {
      const b2ZoneIds = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28];
      for (const zoneId of b2ZoneIds) {
        const path = buildWaypoints(0, 0, 'B2', zoneId);
        for (const p of path) {
          expect(p.x).toBeGreaterThanOrEqual(0);
          expect(p.x).toBeLessThanOrEqual(1);
          expect(p.y).toBeGreaterThanOrEqual(0);
          expect(p.y).toBeLessThanOrEqual(1);
        }
      }
    });
  });
});
