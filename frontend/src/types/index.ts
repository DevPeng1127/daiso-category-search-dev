export type Screen = 'home' | 'loading' | 'results' | 'map' | 'category' | 'category-map' | 'storemap' | 'help';

export interface Product {
  id: number;
  rank: number;
  name: string;
  price: number;
  image_url: string;
  category_major: string | null;
  category_middle: string | null;
  score: number;
  counter_number?: number | null;
  destination_x?: number | null;
  destination_y?: number | null;
  location_floor?: string | null;
  location_description?: string | null;
  zone_id?: number | null;
}

export interface Waypoint {
  x: number;
  y: number;
}

export interface MapInfo {
  floor: string;
  section: string;
  map_image: string;
  counter_number?: number | null;
  section_description?: string;
  destination?: Waypoint | null;
  start?: Waypoint | null;
  waypoints?: Waypoint[];
}

export interface QueryInfo {
  original: string;
  intent: string;
  keywords: string[];
}

export interface SearchResponse {
  results: Product[];
  map_info: MapInfo | null;
  query_info: QueryInfo | null;
  message?: string | null;
  is_recommendation?: boolean;
}

export interface Category {
  major: string;
  middles: string[];
}

export interface ShareResponse {
  product: Product;
  map_info: MapInfo;
}

export interface HealthStatus {
  status: string;
  services: Record<string, boolean>;
}
