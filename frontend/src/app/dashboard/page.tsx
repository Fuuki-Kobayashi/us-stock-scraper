"use client";

import { SurgeSummaryCards } from "@/components/surges/SurgeSummaryCards";
import { SurgeTrendChart } from "@/components/charts/SurgeTrendChart";
import { SectorDistChart } from "@/components/charts/SectorDistChart";
import { DayOfWeekChart } from "@/components/charts/DayOfWeekChart";
import { useSurgeStats, useTodaySurges } from "@/hooks/useSurges";
import { formatPercent, formatDate, percentColorClass } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  const { data: stats, isLoading: statsLoading } = useSurgeStats();
  const { data: todaySurges, isLoading: todayLoading } = useTodaySurges();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <SurgeSummaryCards />

      <div className="grid gap-6 lg:grid-cols-2">
        {stats && <SurgeTrendChart data={stats.monthly_trend} />}
        {stats && <SectorDistChart data={stats.sector_distribution} />}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {stats && <DayOfWeekChart data={stats.day_of_week} />}

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Top Repeat Surgers
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead className="text-right">Count</TableHead>
                    <TableHead className="text-right">Avg Change</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stats?.top_repeat_surgers?.slice(0, 10).map((s) => (
                    <TableRow
                      key={s.symbol}
                      className="cursor-pointer hover:bg-accent/50"
                      onClick={() => router.push(`/stocks/${s.symbol}`)}
                    >
                      <TableCell className="font-medium">{s.symbol}</TableCell>
                      <TableCell className="max-w-[150px] truncate">
                        {s.name}
                      </TableCell>
                      <TableCell className="text-right">{s.count}</TableCell>
                      <TableCell
                        className={cn(
                          "text-right",
                          percentColorClass(s.avg_change_pct)
                        )}
                      >
                        {formatPercent(s.avg_change_pct)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Today&apos;s Top Surges
          </CardTitle>
        </CardHeader>
        <CardContent>
          {todayLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : todaySurges && todaySurges.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Change%</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {todaySurges.slice(0, 10).map((s) => (
                  <TableRow
                    key={s.id}
                    className="cursor-pointer hover:bg-accent/50"
                    onClick={() => router.push(`/stocks/${s.symbol}`)}
                  >
                    <TableCell className="font-medium">{s.symbol}</TableCell>
                    <TableCell className="max-w-[150px] truncate">
                      {s.name}
                    </TableCell>
                    <TableCell>{formatDate(s.date)}</TableCell>
                    <TableCell
                      className={cn(
                        "text-right font-medium",
                        percentColorClass(s.change_pct)
                      )}
                    >
                      {formatPercent(s.change_pct)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-sm text-muted-foreground">
              No surges detected today.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
