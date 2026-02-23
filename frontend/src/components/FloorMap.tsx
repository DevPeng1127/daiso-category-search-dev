import { useRef, useState, useCallback, useEffect } from 'react';
import type { MapInfo } from '../types';
import NavigationOverlay from './NavigationOverlay';

interface FloorMapProps {
  mapInfo: MapInfo;
}

interface ImgRect {
  width: number;
  height: number;
  offsetX: number;
  offsetY: number;
}

export default function FloorMap({ mapInfo }: FloorMapProps) {
  const imgRef = useRef<HTMLImageElement>(null);
  const [imgRect, setImgRect] = useState<ImgRect | null>(null);

  const measure = useCallback(() => {
    if (!imgRef.current) return;
    const img = imgRef.current;
    const containerW = img.clientWidth;
    const containerH = img.clientHeight;
    const naturalW = img.naturalWidth;
    const naturalH = img.naturalHeight;

    if (containerW === 0 || containerH === 0 || naturalW === 0 || naturalH === 0) return;

    // object-contain scales the image to fit while preserving aspect ratio
    const scale = Math.min(containerW / naturalW, containerH / naturalH);
    const renderedW = naturalW * scale;
    const renderedH = naturalH * scale;
    const offsetX = (containerW - renderedW) / 2;
    const offsetY = (containerH - renderedH) / 2;

    setImgRect({ width: renderedW, height: renderedH, offsetX, offsetY });
  }, []);

  // Handle cached images (onLoad may not fire) + recalculate on resize
  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;

    // If already loaded (cached), measure immediately
    if (img.complete && img.naturalWidth > 0) {
      measure();
    }

    // Recalculate when container resizes
    const ro = new ResizeObserver(() => {
      if (img.complete && img.naturalWidth > 0) {
        measure();
      }
    });
    ro.observe(img);

    return () => ro.disconnect();
  }, [measure]);

  return (
    <div className="relative w-full h-full">
      {/* Floor label */}
      <span className="absolute top-3 left-3 z-10 text-lg font-bold text-gray-700">
        {mapInfo.floor}
      </span>

      <img
        ref={imgRef}
        src={mapInfo.map_image}
        alt="매장 지도"
        className="w-full h-full object-contain"
        onLoad={measure}
        onError={(e) => {
          (e.target as HTMLImageElement).src = '';
          (e.target as HTMLImageElement).alt = '지도를 불러올 수 없습니다';
        }}
      />

      {imgRect && imgRect.width > 0 && mapInfo.waypoints && mapInfo.waypoints.length > 0 && mapInfo.destination && mapInfo.start && (
        <NavigationOverlay
          waypoints={mapInfo.waypoints}
          destination={mapInfo.destination}
          start={mapInfo.start}
          sectionName={mapInfo.section_description ?? null}
          width={imgRect.width}
          height={imgRect.height}
          offsetX={imgRect.offsetX}
          offsetY={imgRect.offsetY}
        />
      )}
    </div>
  );
}
