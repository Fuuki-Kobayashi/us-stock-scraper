"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  ColorType,
  CandlestickSeries,
  HistogramSeries,
  createSeriesMarkers,
  type IChartApi,
} from "lightweight-charts";
import type { OHLCVData } from "@/types";

interface StockChartProps {
  data: OHLCVData[];
  surgeMarkers?: { time: string; label: string }[];
}

export function StockChart({ data, surgeMarkers }: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#9ca3af",
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.05)" },
        horzLines: { color: "rgba(255,255,255,0.05)" },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      crosshair: {
        mode: 0,
      },
      timeScale: {
        borderColor: "rgba(255,255,255,0.1)",
      },
      rightPriceScale: {
        borderColor: "rgba(255,255,255,0.1)",
      },
    });

    chartRef.current = chart;

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#10b981",
      downColor: "#ef4444",
      borderUpColor: "#10b981",
      borderDownColor: "#ef4444",
      wickUpColor: "#10b981",
      wickDownColor: "#ef4444",
    });

    candleSeries.setData(
      data.map((d) => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }))
    );

    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: "#6366f1",
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    volumeSeries.setData(
      data.map((d) => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)",
      }))
    );

    if (surgeMarkers && surgeMarkers.length > 0) {
      const markers = surgeMarkers.map((m) => ({
        time: m.time,
        position: "aboveBar" as const,
        color: "#f59e0b",
        shape: "arrowDown" as const,
        text: m.label,
      }));
      createSeriesMarkers(candleSeries, markers);
    }

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [data, surgeMarkers]);

  return <div ref={chartContainerRef} className="w-full" />;
}
