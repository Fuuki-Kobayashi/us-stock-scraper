import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchSettings, updateSettings } from "@/lib/api";
import type { UserSettings } from "@/types";

export function useSettings() {
  return useQuery<UserSettings>({
    queryKey: ["settings"],
    queryFn: () => fetchSettings() as Promise<UserSettings>,
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { surge_threshold: number }) => updateSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
  });
}
