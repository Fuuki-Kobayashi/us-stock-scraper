"use client";

import { useState, useMemo } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StockChart } from "@/components/charts/StockChart";
import { useStockChart } from "@/hooks/useStockChart";
import { useSurges } from "@/hooks/useSurges";
import {
  formatDate,
  formatPercent,
  formatVolume,
  formatPrice,
  percentColorClass,
} from "@/lib/formatters";
import { cn } from "@/lib/utils";
import { subMonths, subYears, format } from "date-fns";
import type { SurgeEvent, PaginatedResponse } from "@/types";

const TIME_RANGES = [
  { label: "1M", months: 1 },
  { label: "3M", months: 3 },
  { label: "6M", months: 6 },
  { label: "1Y", months: 12 },
  { label: "2Y", months: 24 },
] as const;

export default function StockDetailPage() {
  const params = useParams();
  const symbol = params.symbol as string;
  const [rangeIdx, setRangeIdx] = useState(2); // default 6M

  const now = new Date();
  const range = TIME_RANGES[rangeIdx];
  const fromDate = format(
    range.months <= 12
      ? subMonths(now, range.months)
      : subYears(now, range.months / 12),
    "yyyy-MM-dd"
  );
  const toDate = format(now, "yyyy-MM-dd");

  const { data: chartData, isLoading: chartLoading } = useStockChart(
    symbol,
    fromDate,
    toDate
  );

  const { data: surgesData } = useSurges({
    page: 1,
    limit: 100,
    sector: undefined,
  });

  const surgesForSymbol = useMemo(() => {
    const paginated = surgesData as PaginatedResponse<SurgeEvent> | undefined;
    if (!paginated) return [];
    return paginated.items.filter(
      (s) => s.symbol.toUpperCase() === symbol.toUpperCase()
    );
  }, [surgesData, symbol]);

  const surgeMarkers = useMemo(
    () =>
      surgesForSymbol.map((s) => ({
        time: s.date,
        label: `Surge ${formatPercent(s.change_pct)}`,
      })),
    [surgesForSymbol]
  );

  const stockInfo = surgesForSymbol[0];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold">{symbol}</h1>
        {stockInfo && (
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">{stockInfo.name}</span>
            {stockInfo.sector && (
              <Badge variant="secondary">{stockInfo.sector}</Badge>
            )}
            {stockInfo.exchange && (
              <Badge variant="outline">{stockInfo.exchange}</Badge>
            )}
          </div>
        )}
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-sm font-medium">Price Chart</CardTitle>
          <div className="flex gap-1">
            {TIME_RANGES.map((r, i) => (
              <Button
                key={r.label}
                variant={i === rangeIdx ? "default" : "outline"}
                size="sm"
                onClick={() => setRangeIdx(i)}
              >
                {r.label}
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          {chartLoading ? (
            <div className="flex h-[400px] items-center justify-center">
              <p className="text-sm text-muted-foreground">Loading chart...</p>
            </div>
          ) : chartData && chartData.length > 0 ? (
            <StockChart data={chartData} surgeMarkers={surgeMarkers} />
          ) : (
            <div className="flex h-[400px] items-center justify-center">
              <p className="text-sm text-muted-foreground">
                No chart data available for this period.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Surge History</CardTitle>
        </CardHeader>
        <CardContent>
          {surgesForSymbol.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Change%</TableHead>
                  <TableHead className="text-right">Open</TableHead>
                  <TableHead className="text-right">Close</TableHead>
                  <TableHead className="text-right">High</TableHead>
                  <TableHead className="text-right">Low</TableHead>
                  <TableHead className="text-right">Volume</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {surgesForSymbol.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell>{formatDate(s.date)}</TableCell>
                    <TableCell
                      className={cn(
                        "text-right font-medium",
                        percentColorClass(s.change_pct)
                      )}
                    >
                      {formatPercent(s.change_pct)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatPrice(s.open)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatPrice(s.close)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatPrice(s.high)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatPrice(s.low)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatVolume(s.volume)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-sm text-muted-foreground">
              No surge events recorded for {symbol}.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
