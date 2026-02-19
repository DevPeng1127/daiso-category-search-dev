import type { Product } from '../types';

interface ProductCardProps {
  product: Product;
  isTop?: boolean;
  onSelect: (product: Product) => void;
}

export default function ProductCard({ product, isTop = false, onSelect }: ProductCardProps) {
  return (
    <button
      onClick={() => onSelect(product)}
      className={`flex flex-col items-center p-8 rounded-3xl transition-all
                  hover:shadow-lg active:scale-[0.98] cursor-pointer bg-white
                  ${isTop
                    ? 'border-3 border-dashed border-daiso-red flex-1'
                    : 'border border-gray-200 flex-1'
                  }`}
      aria-label={`${product.name} 위치 보기`}
    >
      {isTop && (
        <span className="text-daiso-red text-sm font-extrabold tracking-wider mb-3">
          BEST!
        </span>
      )}
      <div className={`mb-4 overflow-hidden rounded-xl bg-gray-50
                       ${isTop ? 'w-60 h-60' : 'w-48 h-48'}`}>
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-contain"
          loading="lazy"
        />
      </div>
      <h3 className={`font-bold text-daiso-gray-900 text-center leading-tight mb-2
                       ${isTop ? 'text-xl' : 'text-lg'}`}>
        {product.name}
      </h3>
      <p className="text-sm text-gray-400">
        {product.category_major} &gt; {product.category_middle}
      </p>
    </button>
  );
}
