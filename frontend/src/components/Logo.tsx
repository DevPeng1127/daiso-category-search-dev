import { useAppStore } from '../stores/useAppStore';

export default function Logo() {
  const reset = useAppStore((s) => s.reset);

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
