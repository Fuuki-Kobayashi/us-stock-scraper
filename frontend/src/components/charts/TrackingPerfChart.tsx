"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SectorTracking } from "@/types";

interface TrackingPerfChartProps {
  data: SectorTracking[];
}

export function TrackingPerfChart({ data }: TrackingPerfChartProps) {
  const chartData = data.map((s) => ({
    sector: s.sector,
    "1 Day": Number(s.avg_1d.toFixed(2)),
    "7 Days": Number(s.avg_7d.toFixed(2)),
    "30 Days": Number(s.avg_30d.toFixed(2)),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">
          Performance by Sector
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="sector"
                tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                angle={-30}
                textAnchor="end"
                height={60}
              />
              <YAxis
                tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  color: "hsl(var(--foreground))",
                }}
                formatter={(value) => `${value ?? 0}%`}
              />
              <Legend />
              <Bar dataKey="1 Day" fill="hsl(var(--chart-1))" radius={[2, 2, 0, 0]} />
              <Bar dataKey="7 Days" fill="hsl(var(--chart-2))" radius={[2, 2, 0, 0]} />
              <Bar dataKey="30 Days" fill="hsl(var(--chart-3))" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
