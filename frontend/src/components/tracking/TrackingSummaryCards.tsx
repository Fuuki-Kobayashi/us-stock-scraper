"use client";

import { StatCard } from "@/components/common/StatCard";
import { useTrackingPerformance } from "@/hooks/useTracking";
import { formatPercent } from "@/lib/formatters";

export function TrackingSummaryCards() {
  const { data } = useTrackingPerformance();

  if (!data) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCard key={i} title="Loading..." value="--" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Avg 1-Day Return"
        value={formatPercent(data.avg_1d)}
        description={`Win rate: ${(data.win_rate_1d * 100).toFixed(1)}%`}
      />
      <StatCard
        title="Avg 7-Day Return"
        value={formatPercent(data.avg_7d)}
        description={`Win rate: ${(data.win_rate_7d * 100).toFixed(1)}%`}
      />
      <StatCard
        title="Avg 30-Day Return"
        value={formatPercent(data.avg_30d)}
        description={`Win rate: ${(data.win_rate_30d * 100).toFixed(1)}%`}
      />
      <StatCard
        title="Total Tracked"
        value={String(data.total_tracked)}
        description="Surge events with tracking"
      />
    </div>
  );
}
