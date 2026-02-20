import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import MapScreen from '../../screens/MapScreen';
import { useAppStore } from '../../stores/useAppStore';

beforeEach(() => {
  useAppStore.setState({
    screen: 'map',
    mapInfo: {
      floor: 'B1',
      section: '뷰티/위생',
      map_image: '/maps/map_b1.jpg',
      counter_number: 11,
      section_description: '화장품',
      destination: { x: 0.82, y: 0.24 },
      start: { x: 0.45, y: 0.05 },
      waypoints: [
        { x: 0.45, y: 0.05 },
        { x: 0.82, y: 0.05 },
        { x: 0.82, y: 0.24 },
      ],
    },
    selectedProduct: {
      id: 1, rank: 1, name: '대용량 물티슈', price: 1000,
      image_url: '/img.jpg', category_major: '뷰티/위생',
      category_middle: '화장지/물티슈', score: 0.95,
      counter_number: 11, destination_x: 0.82, destination_y: 0.24,
      location_floor: 'B1', location_description: '화장품', zone_id: 11,
    },
  });
});

describe('MapScreen', () => {
  it('should render map title', () => {
    render(<MapScreen />);
    expect(screen.getByText('매장 지도')).toBeInTheDocument();
  });

  it('should show counter number in location text', () => {
    render(<MapScreen />);
    expect(screen.getByText(/11번 매대/)).toBeInTheDocument();
  });

  it('should show floor label', () => {
    render(<MapScreen />);
    expect(screen.getByText(/지하1층/)).toBeInTheDocument();
  });

  it('should render reset button', () => {
    render(<MapScreen />);
    expect(screen.getByText('다시 검색하기')).toBeInTheDocument();
  });

  it('should reset on button click', () => {
    render(<MapScreen />);
    fireEvent.click(screen.getByText('다시 검색하기'));
    expect(useAppStore.getState().screen).toBe('home');
  });

  it('should show QR scan description', () => {
    render(<MapScreen />);
    expect(screen.getByText(/QR코드를 스캔하면/)).toBeInTheDocument();
  });

  it('should render logo', () => {
    render(<MapScreen />);
    expect(screen.getByAltText('어디다이소')).toBeInTheDocument();
  });

  it('should render back-to-results button', () => {
    render(<MapScreen />);
    expect(screen.getByText('검색 결과로 돌아가기')).toBeInTheDocument();
  });

  it('should go back to results on button click', () => {
    useAppStore.setState({ results: [{ id: 1, rank: 1, name: '물티슈', price: 1000, image_url: '/img.jpg', category_major: null, category_middle: null, score: 0.9 }] });
    render(<MapScreen />);
    fireEvent.click(screen.getByText('검색 결과로 돌아가기'));
    expect(useAppStore.getState().screen).toBe('results');
  });

  it('should hide back-to-results and reset buttons in shared mode', () => {
    useAppStore.setState({ isSharedMode: true });
    render(<MapScreen />);
    expect(screen.queryByText('검색 결과로 돌아가기')).not.toBeInTheDocument();
    expect(screen.queryByText('다시 검색하기')).not.toBeInTheDocument();
  });

  it('should hide QR section in shared mode', () => {
    useAppStore.setState({ isSharedMode: true });
    render(<MapScreen />);
    expect(screen.queryByText(/QR코드를 스캔하면/)).not.toBeInTheDocument();
  });

  it('should show product name in shared mode', () => {
    useAppStore.setState({ isSharedMode: true });
    render(<MapScreen />);
    expect(screen.getByText('대용량 물티슈')).toBeInTheDocument();
  });
});
