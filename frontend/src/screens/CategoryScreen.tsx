import { useAppStore } from '../stores/useAppStore';
import { B1_ZONES, B2_ZONES } from '../utils/pathfinding';
import Logo from '../components/Logo';
import BottomNav from '../components/BottomNav';

export default function CategoryScreen() {
  const selectZone = useAppStore((s) => s.selectZone);

  const b1Entries = Object.entries(B1_ZONES).map(([id, zone]) => ({
    id: Number(id),
    name: zone.name,
    floor: 'B1',
  }));

  const b2Entries = Object.entries(B2_ZONES).map(([id, zone]) => ({
    id: Number(id),
    name: zone.name,
    floor: 'B2',
  }));

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="px-8 pt-6 pb-2">
        <Logo />
      </header>

      {/* Title */}
      <h2 className="text-center text-2xl font-extrabold text-daiso-gray-900 mb-6">
        카테고리별 안내
      </h2>

      {/* Content */}
      <main className="flex-1 overflow-y-auto px-8 pb-8">
        <div className="max-w-3xl mx-auto space-y-8">
          {/* B1 Section */}
          <section>
            <h3 className="text-xl font-bold text-daiso-gray-900 mb-4">지하1층</h3>
            <div className="grid grid-cols-4 gap-4">
              {b1Entries.map((entry) => (
                <button
                  key={entry.id}
                  onClick={() => selectZone(entry.id, entry.floor, entry.name)}
                  className="px-5 py-4 rounded-xl bg-red-50 text-daiso-gray-900 font-bold
                             hover:bg-daiso-red hover:text-white active:scale-95 transition-all text-base"
                >
                  {entry.name}
                </button>
              ))}
            </div>
          </section>

          {/* B2 Section */}
          <section>
            <h3 className="text-xl font-bold text-daiso-gray-900 mb-4">지하2층</h3>
            <div className="grid grid-cols-4 gap-4">
              {b2Entries.map((entry) => (
                <button
                  key={entry.id}
                  onClick={() => selectZone(entry.id, entry.floor, entry.name)}
                  className="px-5 py-4 rounded-xl bg-blue-50 text-daiso-gray-900 font-bold
                             hover:bg-blue-500 hover:text-white active:scale-95 transition-all text-base"
                >
                  {entry.name}
                </button>
              ))}
            </div>
          </section>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
