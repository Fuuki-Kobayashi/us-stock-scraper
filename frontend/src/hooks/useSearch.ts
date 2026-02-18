import { useQuery } from "@tanstack/react-query";
import { fetchSearch } from "@/lib/api";
import type { SearchResult } from "@/types";

interface SearchResponse {
  results: SearchResult[];
  count: number;
}

export function useSearch(query: string) {
  return useQuery<SearchResult[]>({
    queryKey: ["search", query],
    queryFn: async () => {
      const res = await fetchSearch(query) as SearchResponse;
      return res.results ?? [];
    },
    enabled: query.length >= 1,
  });
}
