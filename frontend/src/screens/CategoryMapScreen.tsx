import { useRef, useState, useCallback } from 'react';
import { useAppStore } from '../stores/useAppStore';
import { B1_ZONES, B2_ZONES } from '../utils/pathfinding';
import Logo from '../components/Logo';

const IMAGE_WIDTH = 863;
const IMAGE_HEIGHT = 1024;

export default function CategoryMapScreen() {
  const selectedZone = useAppStore((s) => s.selectedZone);
  const setScreen = useAppStore((s) => s.setScreen);
  const imgRef = useRef<HTMLImageElement>(null);
  const [imgRect, setImgRect] = useState<{ width: number; height: number; offsetX: number; offsetY: number } | null>(null);

  const handleImageLoad = useCallback(() => {
    if (!imgRef.current) return;
    const img = imgRef.current;
    const containerW = img.clientWidth;
    const containerH = img.clientHeight;
    const naturalW = img.naturalWidth;
    const naturalH = img.naturalHeight;
    const scale = Math.min(containerW / naturalW, containerH / naturalH);
    const renderedW = naturalW * scale;
    const renderedH = naturalH * scale;
    const offsetX = (containerW - renderedW) / 2;
    const offsetY = (containerH - renderedH) / 2;
    setImgRect({ width: renderedW, height: renderedH, offsetX, offsetY });
  }, []);

  if (!selectedZone) return null;

  const zones = selectedZone.floor === 'B1' ? B1_ZONES : B2_ZONES;
  const zone = zones[selectedZone.id];
  const mapImage = `/maps/map_${selectedZone.floor.toLowerCase()}.jpg`;
  const floorLabel = selectedZone.floor === 'B1' ? '지하1층' : '지하2층';

  // Normalized pin position
  const pinX = zone ? zone.x / IMAGE_WIDTH : 0;
  const pinY = zone ? zone.y / IMAGE_HEIGHT : 0;

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="px-8 pt-6 pb-2">
        <Logo />
      </header>

      {/* Title + Floor */}
      <div className="text-center mb-4">
        <h2 className="text-2xl font-extrabold text-daiso-gray-900">
          {selectedZone.name}
        </h2>
        <p className="text-base text-gray-500 mt-1">{floorLabel}</p>
      </div>

      {/* Map */}
      <main className="flex-1 mx-8 mb-4 border border-gray-200 rounded-2xl overflow-hidden bg-gray-50 min-h-0 relative">
        <img
          ref={imgRef}
          src={mapImage}
          alt="매장 지도"
          className="w-full h-full object-contain"
          onLoad={handleImageLoad}
        />

        {/* Pin marker */}
        {imgRect && imgRect.width > 0 && (
          <div
            data-testid="zone-pin"
            className="absolute flex flex-col items-center"
            style={{
              left: imgRect.offsetX + pinX * imgRect.width - 16,
              top: imgRect.offsetY + pinY * imgRect.height - 40,
            }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#E53E3E" className="w-8 h-8 drop-shadow-lg">
              <path fillRule="evenodd" d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
            </svg>
            <span className="text-xs font-bold text-red-600 bg-white/90 px-2 py-0.5 rounded shadow mt-0.5">
              {selectedZone.name}
            </span>
          </div>
        )}
      </main>

      {/* Back button */}
      <div className="flex justify-center pb-6">
        <button
          onClick={() => setScreen('category')}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gray-400 text-white
                     font-bold hover:bg-gray-500 active:scale-95 transition-all"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
          </svg>
          뒤로가기
        </button>
      </div>
    </div>
  );
}
