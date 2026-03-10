const BASE = import.meta.env.VITE_API_URL || "";

export interface ZoneForecast {
  zone_id: string;
  zone_name: string;
  issued: string | null;
  expires: string | null;
  forecast_text: string;
  has_active_advisory: boolean;
  has_upcoming_advisory: boolean;
  advisory_text: string | null;
  fetched_at: string;
}

export interface AllForecastsResponse {
  total_zones: number;
  successful: number;
  failed: number;
  forecasts: ZoneForecast[];
  errors: { zone_id: string; error: string }[] | null;
  cache_last_updated: string | null;
  cache_next_update: string | null;
}

export interface CacheStatus {
  last_updated: string | null;
  next_update: string | null;
  update_interval_minutes: number;
  total_updates: number;
  last_update_duration_seconds: number | null;
  zones_cached: number;
  zones_failed: number;
  health: string;
}

export interface ServerSettings {
  cache_interval_minutes: number;
  auth_enabled: boolean;
  mcp_enabled: boolean;
  allowed_origins: string[];
  log_level: string;
  noaa_base_url: string;
  uw_synopsis_url: string;
}

function headers(): HeadersInit {
  const h: HeadersInit = { "Content-Type": "application/json" };
  const key = localStorage.getItem("api_key");
  if (key) h["X-API-Key"] = key;
  return h;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: headers() });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: headers(),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  forecasts: () => get<AllForecastsResponse>("/api/v1/forecast"),
  forecast: (id: string) => get<ZoneForecast>(`/api/v1/forecast/${id}`),
  status: () => get<CacheStatus>("/api/v1/status"),
  settings: () => get<ServerSettings>("/api/v1/settings"),
  refresh: () => post<{ message: string }>("/api/v1/cache/refresh"),
};
