import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CategoryScreen from '../../screens/CategoryScreen';
import { useAppStore } from '../../stores/useAppStore';

beforeEach(() => {
  useAppStore.setState({ screen: 'category', selectedZone: null });
});

describe('CategoryScreen', () => {
  it('should render title', () => {
    render(<CategoryScreen />);
    expect(screen.getByText('카테고리별 안내')).toBeInTheDocument();
  });

  it('should render B1 section header', () => {
    render(<CategoryScreen />);
    expect(screen.getByText('지하1층')).toBeInTheDocument();
  });

  it('should render B2 section header', () => {
    render(<CategoryScreen />);
    expect(screen.getByText('지하2층')).toBeInTheDocument();
  });

  it('should render B1 zone buttons', () => {
    render(<CategoryScreen />);
    expect(screen.getByText('화장품')).toBeInTheDocument();
    expect(screen.getByText('식품')).toBeInTheDocument();
    expect(screen.getByText('문구')).toBeInTheDocument();
  });

  it('should render B2 zone buttons', () => {
    render(<CategoryScreen />);
    expect(screen.getByText('욕실')).toBeInTheDocument();
    expect(screen.getByText('주방')).toBeInTheDocument();
    expect(screen.getByText('스포츠')).toBeInTheDocument();
  });

  it('should navigate to category-map on zone click', () => {
    render(<CategoryScreen />);
    fireEvent.click(screen.getByText('화장품'));
    const state = useAppStore.getState();
    expect(state.screen).toBe('category-map');
    expect(state.selectedZone?.name).toBe('화장품');
    expect(state.selectedZone?.floor).toBe('B1');
  });

  it('should render logo', () => {
    render(<CategoryScreen />);
    expect(screen.getByAltText('어디다이소')).toBeInTheDocument();
  });

  it('should render BottomNav', () => {
    render(<CategoryScreen />);
    expect(screen.getByText('홈')).toBeInTheDocument();
  });
});
