import { useQuery } from "@tanstack/react-query";
import { fetchStockChart } from "@/lib/api";
import type { OHLCVData } from "@/types";

export function useStockChart(symbol: string, from?: string, to?: string) {
  return useQuery<OHLCVData[]>({
    queryKey: ["stockChart", symbol, from, to],
    queryFn: () => fetchStockChart(symbol, from, to) as Promise<OHLCVData[]>,
    enabled: !!symbol,
  });
}
