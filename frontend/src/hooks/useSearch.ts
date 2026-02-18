import { useQuery } from "@tanstack/react-query";
import { fetchSearch } from "@/lib/api";
import type { SearchResult } from "@/types";

export function useSearch(query: string) {
  return useQuery<SearchResult[]>({
    queryKey: ["search", query],
    queryFn: () => fetchSearch(query) as Promise<SearchResult[]>,
    enabled: query.length >= 1,
  });
}
