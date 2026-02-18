import { format, parseISO } from "date-fns";

export function formatDate(dateStr: string): string {
  return format(parseISO(dateStr), "yyyy-MM-dd");
}

export function formatDateTime(dateStr: string): string {
  return format(parseISO(dateStr), "yyyy-MM-dd HH:mm");
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

export function formatVolume(value: number): string {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value);
}

export function formatPrice(value: number): string {
  return `$${value.toFixed(2)}`;
}

export function percentColorClass(value: number): string {
  if (value > 0) return "text-emerald-500";
  if (value < 0) return "text-red-500";
  return "text-muted-foreground";
}
