"use client";

import { useRouter } from "next/navigation";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ArrowUpDown } from "lucide-react";
import { formatDate, formatPercent, formatVolume, formatPrice, percentColorClass } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type { SurgeEvent } from "@/types";

interface SurgeTableProps {
  data: SurgeEvent[];
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const columns: ColumnDef<SurgeEvent>[] = [
  {
    accessorKey: "date",
    header: ({ column }) => (
      <Button
        variant="ghost"
        size="sm"
        className="-ml-3"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Date <ArrowUpDown className="ml-1 h-3 w-3" />
      </Button>
    ),
    cell: ({ row }) => formatDate(row.getValue("date")),
  },
  {
    accessorKey: "symbol",
    header: "Symbol",
    cell: ({ row }) => (
      <span className="font-medium">{row.getValue("symbol")}</span>
    ),
  },
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <span className="max-w-[200px] truncate block">
        {row.getValue("name")}
      </span>
    ),
  },
  {
    accessorKey: "sector",
    header: "Sector",
  },
  {
    accessorKey: "change_pct",
    header: ({ column }) => (
      <Button
        variant="ghost"
        size="sm"
        className="-ml-3"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Change% <ArrowUpDown className="ml-1 h-3 w-3" />
      </Button>
    ),
    cell: ({ row }) => {
      const val = row.getValue<number>("change_pct");
      return (
        <span className={cn("font-medium", percentColorClass(val))}>
          {formatPercent(val)}
        </span>
      );
    },
  },
  {
    accessorKey: "volume",
    header: ({ column }) => (
      <Button
        variant="ghost"
        size="sm"
        className="-ml-3"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Volume <ArrowUpDown className="ml-1 h-3 w-3" />
      </Button>
    ),
    cell: ({ row }) => formatVolume(row.getValue("volume")),
  },
  {
    accessorKey: "open",
    header: "Open",
    cell: ({ row }) => formatPrice(row.getValue("open")),
  },
  {
    accessorKey: "close",
    header: "Close",
    cell: ({ row }) => formatPrice(row.getValue("close")),
  },
  {
    accessorKey: "high",
    header: "High",
    cell: ({ row }) => formatPrice(row.getValue("high")),
  },
  {
    accessorKey: "low",
    header: "Low",
    cell: ({ row }) => formatPrice(row.getValue("low")),
  },
];

export function SurgeTable({ data, page, totalPages, onPageChange }: SurgeTableProps) {
  const router = useRouter();
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: { sorting },
  });

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  className="cursor-pointer hover:bg-accent/50"
                  onClick={() => router.push(`/stocks/${row.original.symbol}`)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Page {page} of {totalPages}
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
