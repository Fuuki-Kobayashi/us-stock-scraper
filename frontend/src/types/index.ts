// Surge event from backend
export interface SurgeEvent {
  id: number;
  symbol: string;
  name: string;
  exchange: string;
  sector: string;
  stock_type: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change_pct: number;
}

// Paginated response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Surge detail includes tracking data
export interface SurgeDetail extends SurgeEvent {
  tracking: TrackingRecord[];
}

// Post-surge tracking record
export interface TrackingRecord {
  id: number;
  surge_id: number;
  symbol: string;
  days_after: number;
  date: string;
  close: number;
  change_from_surge: number;
}

// Statistics from /api/surges/stats
export interface SurgeStats {
  sector_distribution: Record<string, number>;
  day_of_week: Record<string, number>;
  monthly_trend: MonthlyTrend[];
  top_repeat_surgers: RepeatSurger[];
}

export interface MonthlyTrend {
  month: string;
  count: number;
}

export interface RepeatSurger {
  symbol: string;
  name: string;
  count: number;
  avg_change_pct: number;
}

// Post-surge performance summary
export interface TrackingPerformance {
  avg_1d: number;
  avg_3d: number;
  avg_7d: number;
  avg_30d: number;
  win_rate_1d: number;
  win_rate_7d: number;
  win_rate_30d: number;
  total_tracked: number;
}

// Tracking by sector
export interface SectorTracking {
  sector: string;
  avg_1d: number;
  avg_3d: number;
  avg_7d: number;
  avg_30d: number;
  count: number;
}

// OHLCV candle data for charts
export interface OHLCVData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// Search result
export interface SearchResult {
  symbol: string;
  name: string;
  exchange: string;
  sector: string;
}

// User settings
export interface UserSettings {
  surge_threshold: number;
}

// Admin status
export interface AdminStatus {
  scheduler_running: boolean;
  next_run: string | null;
  last_run: string | null;
  last_run_status: string | null;
}

// Collection log entry
export interface CollectionLog {
  id: number;
  date: string;
  status: string;
  surges_found: number;
  started_at: string;
  completed_at: string | null;
  error: string | null;
}

// Surge filter parameters
export interface SurgeFilters {
  page?: number;
  limit?: number;
  from_date?: string;
  to_date?: string;
  min_pct?: number;
  sector?: string;
}
