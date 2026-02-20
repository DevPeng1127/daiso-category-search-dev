import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import HelpScreen from '../../screens/HelpScreen';
import { useAppStore } from '../../stores/useAppStore';

beforeEach(() => {
  useAppStore.setState({ screen: 'help' });
});

describe('HelpScreen', () => {
  it('should render help title', () => {
    render(<HelpScreen />);
    expect(screen.getByRole('heading', { name: '도움말' })).toBeInTheDocument();
  });

  it('should render search method section', () => {
    render(<HelpScreen />);
    expect(screen.getByText('검색 방법')).toBeInTheDocument();
  });

  it('should render search examples section', () => {
    render(<HelpScreen />);
    expect(screen.getByText('검색 예시')).toBeInTheDocument();
  });

  it('should render results section', () => {
    render(<HelpScreen />);
    expect(screen.getByText('결과 확인')).toBeInTheDocument();
  });

  it('should render navigation section', () => {
    render(<HelpScreen />);
    expect(screen.getByText('길안내')).toBeInTheDocument();
  });

  it('should render QR section', () => {
    render(<HelpScreen />);
    expect(screen.getByText('QR 이용')).toBeInTheDocument();
  });

  it('should render logo', () => {
    render(<HelpScreen />);
    expect(screen.getByAltText('어디다이소')).toBeInTheDocument();
  });

  it('should render BottomNav', () => {
    render(<HelpScreen />);
    expect(screen.getByText('홈')).toBeInTheDocument();
  });
});
