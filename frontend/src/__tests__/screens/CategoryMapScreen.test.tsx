import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CategoryMapScreen from '../../screens/CategoryMapScreen';
import { useAppStore } from '../../stores/useAppStore';

beforeEach(() => {
  useAppStore.setState({
    screen: 'category-map',
    selectedZone: { id: 11, floor: 'B1', name: '화장품' },
  });
});

describe('CategoryMapScreen', () => {
  it('should render zone name', () => {
    render(<CategoryMapScreen />);
    expect(screen.getByText('화장품')).toBeInTheDocument();
  });

  it('should render floor label', () => {
    render(<CategoryMapScreen />);
    expect(screen.getByText(/지하1층/)).toBeInTheDocument();
  });

  it('should render back button', () => {
    render(<CategoryMapScreen />);
    expect(screen.getByText('뒤로가기')).toBeInTheDocument();
  });

  it('should go back to category screen on back click', () => {
    render(<CategoryMapScreen />);
    fireEvent.click(screen.getByText('뒤로가기'));
    expect(useAppStore.getState().screen).toBe('category');
  });

  it('should render map image', () => {
    render(<CategoryMapScreen />);
    const img = screen.getByAltText('매장 지도');
    expect(img).toBeInTheDocument();
    expect(img.getAttribute('src')).toBe('/maps/map_b1.jpg');
  });

  it('should render B2 map for B2 zone', () => {
    useAppStore.setState({
      selectedZone: { id: 19, floor: 'B2', name: '욕실' },
    });
    render(<CategoryMapScreen />);
    const img = screen.getByAltText('매장 지도');
    expect(img.getAttribute('src')).toBe('/maps/map_b2.jpg');
  });

  it('should render pin marker after image load', () => {
    // Mock image dimensions for onLoad
    Object.defineProperty(HTMLImageElement.prototype, 'clientWidth', { value: 863, configurable: true });
    Object.defineProperty(HTMLImageElement.prototype, 'clientHeight', { value: 1024, configurable: true });
    Object.defineProperty(HTMLImageElement.prototype, 'naturalWidth', { value: 863, configurable: true });
    Object.defineProperty(HTMLImageElement.prototype, 'naturalHeight', { value: 1024, configurable: true });

    render(<CategoryMapScreen />);
    const img = screen.getByAltText('매장 지도');
    fireEvent.load(img);
    expect(screen.getByTestId('zone-pin')).toBeInTheDocument();
  });
});
