import { useQuery } from "@tanstack/react-query";
import { fetchSurges, fetchTodaySurges, fetchSurgeDetail, fetchSurgeStats } from "@/lib/api";
import type { PaginatedResponse, SurgeEvent, SurgeDetail, SurgeStats, SurgeFilters } from "@/types";

export function useSurges(filters: SurgeFilters) {
  return useQuery<PaginatedResponse<SurgeEvent>>({
    queryKey: ["surges", filters],
    queryFn: () => fetchSurges(filters as Record<string, string | number | undefined>) as Promise<PaginatedResponse<SurgeEvent>>,
  });
}

export function useTodaySurges() {
  return useQuery<SurgeEvent[]>({
    queryKey: ["surges", "today"],
    queryFn: () => fetchTodaySurges() as Promise<SurgeEvent[]>,
  });
}

export function useSurgeDetail(id: number) {
  return useQuery<SurgeDetail>({
    queryKey: ["surges", id],
    queryFn: () => fetchSurgeDetail(id) as Promise<SurgeDetail>,
    enabled: id > 0,
  });
}

export function useSurgeStats() {
  return useQuery<SurgeStats>({
    queryKey: ["surges", "stats"],
    queryFn: () => fetchSurgeStats() as Promise<SurgeStats>,
  });
}
