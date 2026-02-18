import { useQuery } from "@tanstack/react-query";
import { fetchTrackingPerformance, fetchTrackingBySector } from "@/lib/api";
import type { TrackingPerformance, SectorTracking } from "@/types";

export function useTrackingPerformance() {
  return useQuery<TrackingPerformance>({
    queryKey: ["tracking", "performance"],
    queryFn: () => fetchTrackingPerformance() as Promise<TrackingPerformance>,
  });
}

export function useTrackingBySector() {
  return useQuery<SectorTracking[]>({
    queryKey: ["tracking", "by-sector"],
    queryFn: () => fetchTrackingBySector() as Promise<SectorTracking[]>,
  });
}
