import { useEffect } from 'react';
import { useAppStore } from './stores/useAppStore';
import HomeScreen from './screens/HomeScreen';
import LoadingScreen from './screens/LoadingScreen';
import ResultsScreen from './screens/ResultsScreen';
import MapScreen from './screens/MapScreen';
import CategoryScreen from './screens/CategoryScreen';
import CategoryMapScreen from './screens/CategoryMapScreen';
import StoreMapScreen from './screens/StoreMapScreen';
import HelpScreen from './screens/HelpScreen';
import IdleTimer from './components/IdleTimer';

function App() {
  const screen = useAppStore((s) => s.screen);
  const initSharedMode = useAppStore((s) => s.initSharedMode);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const isShare = params.get('share');
    const pid = params.get('pid');
    if (isShare === '1' && pid) {
      initSharedMode(Number(pid));
    }
  }, [initSharedMode]);

  return (
    <>
      <IdleTimer />
      {screen === 'home' && <HomeScreen />}
      {screen === 'loading' && <LoadingScreen />}
      {screen === 'results' && <ResultsScreen />}
      {screen === 'map' && <MapScreen />}
      {screen === 'category' && <CategoryScreen />}
      {screen === 'category-map' && <CategoryMapScreen />}
      {screen === 'storemap' && <StoreMapScreen />}
      {screen === 'help' && <HelpScreen />}
    </>
  );
}

export default App;
