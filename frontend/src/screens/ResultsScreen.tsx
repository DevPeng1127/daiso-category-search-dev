import { useAppStore } from '../stores/useAppStore';
import ProductCard from '../components/ProductCard';
import Logo from '../components/Logo';
import BottomNav from '../components/BottomNav';

export default function ResultsScreen() {
  const results = useAppStore((s) => s.results);
  const queryInfo = useAppStore((s) => s.queryInfo);
  const selectProduct = useAppStore((s) => s.selectProduct);
  const isRecommendation = useAppStore((s) => s.isRecommendation);

  // Reorder: put BEST (index 0) in the center (only in normal mode)
  const reordered = !isRecommendation && results.length >= 3
    ? [results[1], results[0], results[2]]
    : results;

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-8 pt-6 pb-4">
        <Logo />
        {queryInfo && (
          <p className="text-lg text-gray-400 font-medium">
            &ldquo;{queryInfo.original}&rdquo; 검색 결과
          </p>
        )}
      </header>

      {/* Recommendation banner */}
      {isRecommendation && (
        <div className="text-center mb-6">
          <p className="text-lg text-gray-500 font-medium">
            찾으시는 상품과 비슷한 상품을 함께 노출합니다
          </p>
        </div>
      )}

      {/* Product cards */}
      <main className="flex-1 flex items-center justify-center">
        <div className="flex items-center justify-center gap-6 w-[80%]">
          {reordered.map((product) => {
            const isTop = !isRecommendation && product.id === results[0]?.id;
            return (
              <ProductCard
                key={product.id}
                product={product}
                isTop={isTop}
                onSelect={selectProduct}
              />
            );
          })}
        </div>
      </main>

      {/* Bottom navigation */}
      <BottomNav />
    </div>
  );
}
