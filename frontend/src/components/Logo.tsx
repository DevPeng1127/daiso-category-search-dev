import { useState, useEffect } from 'react';
import { useAppStore } from '../stores/useAppStore';

/** Detect if the browser has actually darkened the page background */
function useIsDarkBackground() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const check = () => {
      const bg = window.getComputedStyle(document.documentElement).backgroundColor;
      const match = bg.match(/\d+/g);
      if (match) {
        const [r, g, b] = match.map(Number);
        // Perceived brightness formula
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        setIsDark(brightness < 128);
      }
    };
    // Delay to let browser dark mode apply first
    const timer = setTimeout(check, 200);
    return () => clearTimeout(timer);
  }, []);

  return isDark;
}

export default function Logo() {
  const reset = useAppStore((s) => s.reset);
  const isSharedMode = useAppStore((s) => s.isSharedMode);
  const isDarkBg = useIsDarkBackground();

  if (isSharedMode) {
    return (
      <div aria-label="어디다이소">
        <img
          src={isDarkBg ? '/logo_dark01.png' : '/logover01.png'}
          alt="어디다이소"
          className="h-10"
        />
      </div>
    );
  }

  return (
    <button onClick={reset} className="cursor-pointer" aria-label="홈으로 돌아가기">
      <img
        src="/logover01.png"
        alt="어디다이소"
        className="h-10"
      />
    </button>
  );
}
