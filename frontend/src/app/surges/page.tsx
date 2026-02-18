"use client";

import { useState } from "react";
import { useSurges } from "@/hooks/useSurges";
import { SurgeTable } from "@/components/surges/SurgeTable";
import { SurgeFilters } from "@/components/surges/SurgeFilters";
import type { SurgeFilters as SurgeFiltersType, PaginatedResponse, SurgeEvent } from "@/types";

export default function SurgesPage() {
  const [filters, setFilters] = useState<SurgeFiltersType>({
    page: 1,
    limit: 20,
  });

  const { data, isLoading } = useSurges(filters);
  const paginated = data as PaginatedResponse<SurgeEvent> | undefined;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Surge Events</h1>

      <SurgeFilters
        filters={filters}
        onFiltersChange={(f) => setFilters({ ...f, page: 1 })}
      />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading surge data...</p>
      ) : paginated ? (
        <SurgeTable
          data={paginated.items}
          page={paginated.page}
          totalPages={paginated.pages}
          onPageChange={(p) => setFilters((prev) => ({ ...prev, page: p }))}
        />
      ) : (
        <p className="text-sm text-muted-foreground">No data available.</p>
      )}
    </div>
  );
}
