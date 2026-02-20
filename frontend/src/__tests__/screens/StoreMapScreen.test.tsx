import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import StoreMapScreen from '../../screens/StoreMapScreen';
import { useAppStore } from '../../stores/useAppStore';

beforeEach(() => {
  useAppStore.setState({ screen: 'storemap' });
});

describe('StoreMapScreen', () => {
  it('should render title', () => {
    render(<StoreMapScreen />);
    expect(screen.getByText('매장 지도')).toBeInTheDocument();
  });

  it('should render B1 floor label', () => {
    render(<StoreMapScreen />);
    expect(screen.getByText('지하1층')).toBeInTheDocument();
  });

  it('should render B2 floor label', () => {
    render(<StoreMapScreen />);
    expect(screen.getByText('지하2층')).toBeInTheDocument();
  });

  it('should render both map images', () => {
    render(<StoreMapScreen />);
    const images = screen.getAllByRole('img');
    const mapImages = images.filter(img => img.getAttribute('alt')?.includes('지도'));
    expect(mapImages.length).toBe(2);
  });

  it('should render logo', () => {
    render(<StoreMapScreen />);
    expect(screen.getByAltText('어디다이소')).toBeInTheDocument();
  });

  it('should render BottomNav', () => {
    render(<StoreMapScreen />);
    expect(screen.getByText('홈')).toBeInTheDocument();
  });
});
