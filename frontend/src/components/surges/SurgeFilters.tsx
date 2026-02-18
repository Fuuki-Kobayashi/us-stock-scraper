"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { SurgeFilters as SurgeFiltersType } from "@/types";

interface SurgeFiltersProps {
  filters: SurgeFiltersType;
  onFiltersChange: (filters: SurgeFiltersType) => void;
}

export function SurgeFilters({ filters, onFiltersChange }: SurgeFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="space-y-1">
        <label className="text-xs text-muted-foreground">From Date</label>
        <Input
          type="date"
          value={filters.from_date ?? ""}
          onChange={(e) =>
            onFiltersChange({ ...filters, from_date: e.target.value || undefined })
          }
          className="w-40"
        />
      </div>
      <div className="space-y-1">
        <label className="text-xs text-muted-foreground">To Date</label>
        <Input
          type="date"
          value={filters.to_date ?? ""}
          onChange={(e) =>
            onFiltersChange({ ...filters, to_date: e.target.value || undefined })
          }
          className="w-40"
        />
      </div>
      <div className="space-y-1">
        <label className="text-xs text-muted-foreground">Min Change %</label>
        <Input
          type="number"
          value={filters.min_pct ?? ""}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              min_pct: e.target.value ? Number(e.target.value) : undefined,
            })
          }
          placeholder="20"
          className="w-24"
        />
      </div>
      <div className="space-y-1">
        <label className="text-xs text-muted-foreground">Sector</label>
        <Input
          value={filters.sector ?? ""}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              sector: e.target.value || undefined,
            })
          }
          placeholder="All sectors"
          className="w-40"
        />
      </div>
      <Button
        variant="outline"
        size="sm"
        onClick={() => onFiltersChange({ page: 1, limit: 20 })}
      >
        Reset
      </Button>
    </div>
  );
}
