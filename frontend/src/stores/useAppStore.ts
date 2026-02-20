import { create } from 'zustand';
import type { Screen, Product, MapInfo, QueryInfo, Waypoint } from '../types';
import { fetchSearch, fetchSharedProduct } from '../services/api';
import { buildWaypoints } from '../utils/pathfinding';

interface SelectedZone {
  id: number;
  floor: string;
  name: string;
}

interface AppState {
  screen: Screen;
  query: string;
  results: Product[];
  selectedProduct: Product | null;
  isListening: boolean;
  mapInfo: MapInfo | null;
  queryInfo: QueryInfo | null;
  error: string | null;
  isRecommendation: boolean;
  isSharedMode: boolean;
  selectedZone: SelectedZone | null;

  search: (query: string) => Promise<void>;
  setScreen: (screen: Screen) => void;
  selectProduct: (product: Product) => void;
  reset: () => void;
  setListening: (listening: boolean) => void;
  setQuery: (query: string) => void;
  selectZone: (zoneId: number, floor: string, name: string) => void;
  initSharedMode: (productId: number) => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  screen: 'home',
  query: '',
  results: [],
  selectedProduct: null,
  isListening: false,
  mapInfo: null,
  queryInfo: null,
  error: null,
  isRecommendation: false,
  isSharedMode: false,
  selectedZone: null,

  search: async (query: string) => {
    set({ query, screen: 'loading', error: null });
    try {
      const response = await fetchSearch(query);
      const message = response.message
        ?? (response.results.length === 0 ? '검색 결과가 없습니다.' : null);
      set({
        results: response.results,
        mapInfo: response.map_info,
        queryInfo: response.query_info,
        isRecommendation: response.is_recommendation ?? false,
        screen: response.results.length > 0 ? 'results' : 'home',
        error: message,
      });
    } catch {
      set({ screen: 'home', error: '검색 중 오류가 발생했습니다.' });
    }
  },

  setScreen: (screen: Screen) => set({ screen }),

  selectProduct: (product: Product) => {
    const state = useAppStore.getState();
    let mapInfo = state.mapInfo;

    // Recalculate mapInfo if product has location data
    if (product.destination_x != null && product.destination_y != null && mapInfo) {
      const floor = product.location_floor ?? mapInfo.floor;
      const path = buildWaypoints(product.destination_x, product.destination_y, floor, product.zone_id ?? undefined);
      const waypoints: Waypoint[] = path.map(p => ({ x: p.x, y: p.y }));
      mapInfo = {
        ...mapInfo,
        floor: product.location_floor ?? mapInfo.floor,
        map_image: `/maps/map_${(product.location_floor ?? mapInfo.floor).toLowerCase()}.jpg`,
        counter_number: product.counter_number,
        section_description: product.location_description ?? '',
        destination: { x: product.destination_x, y: product.destination_y },
        start: path[0],
        waypoints,
      };
    }

    set({ selectedProduct: product, mapInfo, screen: 'map' });
  },

  reset: () =>
    set({
      screen: 'home',
      query: '',
      results: [],
      selectedProduct: null,
      isListening: false,
      mapInfo: null,
      queryInfo: null,
      error: null,
      isRecommendation: false,
      isSharedMode: false,
      selectedZone: null,
    }),

  setListening: (listening: boolean) => set({ isListening: listening }),

  setQuery: (query: string) => set({ query }),

  selectZone: (zoneId: number, floor: string, name: string) =>
    set({ selectedZone: { id: zoneId, floor, name }, screen: 'category-map' }),

  initSharedMode: async (productId: number) => {
    set({ isSharedMode: true, screen: 'loading' });
    try {
      const data = await fetchSharedProduct(productId);
      set({
        selectedProduct: data.product,
        mapInfo: data.map_info,
        screen: 'map',
      });
    } catch {
      set({ screen: 'home', error: '공유 정보를 불러올 수 없습니다.', isSharedMode: false });
    }
  },
}));
