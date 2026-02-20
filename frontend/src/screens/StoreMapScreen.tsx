import Logo from '../components/Logo';
import BottomNav from '../components/BottomNav';

export default function StoreMapScreen() {
  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="px-8 pt-6 pb-2">
        <Logo />
      </header>

      {/* Title */}
      <h2 className="text-center text-2xl font-extrabold text-daiso-gray-900 mb-6">
        매장 지도
      </h2>

      {/* Maps */}
      <main className="flex-1 flex items-center justify-center gap-8 px-8 pb-4 min-h-0">
        <div className="flex flex-col items-center min-h-0 max-h-full">
          <span className="text-lg font-bold text-daiso-gray-900 mb-2 shrink-0">지하1층</span>
          <img src="/maps/map_b1.jpg" alt="지하1층 지도"
            className="min-h-0 max-h-full object-contain border border-gray-200 rounded-2xl" />
        </div>

        <div className="flex flex-col items-center min-h-0 max-h-full">
          <span className="text-lg font-bold text-daiso-gray-900 mb-2 shrink-0">지하2층</span>
          <img src="/maps/map_b2.jpg" alt="지하2층 지도"
            className="min-h-0 max-h-full object-contain border border-gray-200 rounded-2xl" />
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
