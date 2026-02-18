import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAdminStatus, triggerCollect, triggerBackfill } from "@/lib/api";
import type { AdminStatus } from "@/types";

export function useAdminStatus() {
  return useQuery<AdminStatus>({
    queryKey: ["admin", "status"],
    queryFn: () => fetchAdminStatus() as Promise<AdminStatus>,
    refetchInterval: 30000,
  });
}

export function useCollect() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (date?: string) => triggerCollect(date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin"] });
      queryClient.invalidateQueries({ queryKey: ["surges"] });
    },
  });
}

export function useBackfill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: { from_date: string; to_date: string }) =>
      triggerBackfill(params.from_date, params.to_date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin"] });
      queryClient.invalidateQueries({ queryKey: ["surges"] });
    },
  });
}
