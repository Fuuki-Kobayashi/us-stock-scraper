const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== ""
  );
  if (entries.length === 0) return "";
  return "?" + new URLSearchParams(
    entries.map(([k, v]) => [k, String(v)])
  ).toString();
}

// Surges
export function fetchSurges(params: Record<string, string | number | undefined>) {
  return fetchApi(`/api/surges/${buildQuery(params)}`);
}

export function fetchTodaySurges() {
  return fetchApi("/api/surges/today");
}

export function fetchSurgeDetail(id: number) {
  return fetchApi(`/api/surges/${id}`);
}

export function fetchSurgeStats() {
  return fetchApi("/api/surges/stats");
}

// Tracking
export function fetchTrackingPerformance() {
  return fetchApi("/api/tracking/");
}

export function fetchTrackingBySector() {
  return fetchApi("/api/tracking/by-sector");
}

// Stocks
export function fetchStockChart(
  symbol: string,
  from?: string,
  to?: string
) {
  const params: Record<string, string | undefined> = { from, to };
  return fetchApi(`/api/stocks/${symbol}/chart${buildQuery(params)}`);
}

// Search
export function fetchSearch(q: string) {
  return fetchApi(`/api/search${buildQuery({ q })}`);
}

// Settings
export function fetchSettings() {
  return fetchApi("/api/settings");
}

export function updateSettings(data: { surge_threshold: number }) {
  return fetchApi("/api/settings", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// Admin
export function fetchAdminStatus() {
  return fetchApi("/api/admin/status");
}

export function triggerCollect(date?: string) {
  return fetchApi(`/api/admin/collect${buildQuery({ date })}`, {
    method: "POST",
  });
}

export function triggerBackfill(from_date: string, to_date: string) {
  return fetchApi(
    `/api/admin/backfill${buildQuery({ from_date, to_date })}`,
    { method: "POST" }
  );
}
