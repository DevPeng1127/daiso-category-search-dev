import { useAppStore } from '../stores/useAppStore';

export default function Logo() {
  const reset = useAppStore((s) => s.reset);
  const isSharedMode = useAppStore((s) => s.isSharedMode);

  if (isSharedMode) {
    return (
      <div aria-label="어디다이소">
        <picture>
          <source srcSet="/logo_dark01.png" media="(prefers-color-scheme: dark)" />
          <img src="/logover01.png" alt="어디다이소" className="h-10" />
        </picture>
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
