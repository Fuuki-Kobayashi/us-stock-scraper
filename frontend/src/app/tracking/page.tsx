"use client";

import { TrackingSummaryCards } from "@/components/tracking/TrackingSummaryCards";
import { TrackingTable } from "@/components/tracking/TrackingTable";
import { TrackingPerfChart } from "@/components/charts/TrackingPerfChart";
import { useTrackingBySector } from "@/hooks/useTracking";

export default function TrackingPage() {
  const { data: sectorData, isLoading } = useTrackingBySector();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Post-Surge Tracking</h1>

      <TrackingSummaryCards />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading tracking data...</p>
      ) : sectorData ? (
        <>
          <TrackingPerfChart data={sectorData} />
          <TrackingTable data={sectorData} />
        </>
      ) : (
        <p className="text-sm text-muted-foreground">No tracking data available.</p>
      )}
    </div>
  );
}
