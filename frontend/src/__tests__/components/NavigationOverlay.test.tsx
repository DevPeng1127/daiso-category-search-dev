import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import NavigationOverlay from '../../components/NavigationOverlay';
import type { Waypoint } from '../../types';

const waypoints: Waypoint[] = [
  { x: 0.5, y: 0.9 },
  { x: 0.5, y: 0.75 },
  { x: 0.25, y: 0.75 },
  { x: 0.25, y: 0.3 },
];

const destination: Waypoint = { x: 0.25, y: 0.3 };
const start: Waypoint = { x: 0.5, y: 0.9 };

describe('NavigationOverlay', () => {
  it('should render SVG element', () => {
    const { container } = render(
      <NavigationOverlay
        waypoints={waypoints}
        destination={destination}
        start={start}
        sectionName="화장품"
        width={600}
        height={400}
        offsetX={0}
        offsetY={0}
      />
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('should render a polyline for the path', () => {
    const { container } = render(
      <NavigationOverlay
        waypoints={waypoints}
        destination={destination}
        start={start}
        sectionName="화장품"
        width={600}
        height={400}
        offsetX={0}
        offsetY={0}
      />
    );
    const polyline = container.querySelector('polyline');
    expect(polyline).toBeTruthy();
    expect(polyline?.getAttribute('stroke-dasharray')).toBeTruthy();
  });

  it('should show section name label at destination', () => {
    const { container } = render(
      <NavigationOverlay
        waypoints={waypoints}
        destination={destination}
        start={start}
        sectionName="식품"
        width={600}
        height={400}
        offsetX={0}
        offsetY={0}
      />
    );
    const texts = container.querySelectorAll('text');
    const labels = Array.from(texts).map(t => t.textContent);
    expect(labels.some(l => l?.includes('식품'))).toBe(true);
  });

  it('should show start marker text', () => {
    const { container } = render(
      <NavigationOverlay
        waypoints={waypoints}
        destination={destination}
        start={start}
        sectionName="문구"
        width={600}
        height={400}
        offsetX={0}
        offsetY={0}
      />
    );
    const texts = container.querySelectorAll('text');
    const labels = Array.from(texts).map(t => t.textContent);
    expect(labels.some(l => l?.includes('현위치'))).toBe(true);
  });

  it('should not render when no waypoints', () => {
    const { container } = render(
      <NavigationOverlay
        waypoints={[]}
        destination={destination}
        start={start}
        sectionName="문구"
        width={600}
        height={400}
        offsetX={0}
        offsetY={0}
      />
    );
    const polyline = container.querySelector('polyline');
    expect(polyline).toBeFalsy();
  });
});
