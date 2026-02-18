"use client";

import { StatCard } from "@/components/common/StatCard";
import { useTodaySurges } from "@/hooks/useSurges";
import { useTrackingPerformance } from "@/hooks/useTracking";
import { formatPercent } from "@/lib/formatters";

export function SurgeSummaryCards() {
  const { data: todaySurges } = useTodaySurges();
  const { data: tracking } = useTrackingPerformance();

  const todayCount = todaySurges?.length ?? 0;
  const avgSurgePct =
    todaySurges && todaySurges.length > 0
      ? todaySurges.reduce((sum, s) => sum + s.change_pct, 0) / todaySurges.length
      : 0;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Today's Surges"
        value={String(todayCount)}
        description="Stocks surging today"
      />
      <StatCard
        title="Avg Surge %"
        value={formatPercent(avgSurgePct)}
        description="Average change today"
      />
      <StatCard
        title="Total Tracked"
        value={String(tracking?.total_tracked ?? 0)}
        description="Stocks with tracking data"
      />
      <StatCard
        title="Win Rate (1d)"
        value={
          tracking && !isNaN(tracking.win_rate_1d)
            ? `${(tracking.win_rate_1d * 100).toFixed(1)}%`
            : "N/A"
        }
        description="Positive after 1 day"
      />
    </div>
  );
}
