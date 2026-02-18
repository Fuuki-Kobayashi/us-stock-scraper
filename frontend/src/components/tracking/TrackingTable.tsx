"use client";

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
import { formatPercent, percentColorClass } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type { SectorTracking } from "@/types";

interface TrackingTableProps {
  data: SectorTracking[];
}

const columns: ColumnDef<SectorTracking>[] = [
  {
    accessorKey: "sector",
    header: "Sector",
    cell: ({ row }) => (
      <span className="font-medium">{row.getValue("sector")}</span>
    ),
  },
  {
    accessorKey: "count",
    header: ({ column }) => (
      <Button
        variant="ghost"
        size="sm"
        className="-ml-3"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Count <ArrowUpDown className="ml-1 h-3 w-3" />
      </Button>
    ),
  },
  {
    accessorKey: "avg_1d",
    header: ({ column }) => (
      <Button
        variant="ghost"
        size="sm"
        className="-ml-3"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Avg 1D <ArrowUpDown className="ml-1 h-3 w-3" />
      </Button>
    ),
    cell: ({ row }) => {
      const val = row.getValue<number>("avg_1d");
      return <span className={cn(percentColorClass(val))}>{formatPercent(val)}</span>;
    },
  },
  {
    accessorKey: "avg_3d",
    header: "Avg 3D",
    cell: ({ row }) => {
      const val = row.getValue<number>("avg_3d");
      return <span className={cn(percentColorClass(val))}>{formatPercent(val)}</span>;
    },
  },
  {
    accessorKey: "avg_7d",
    header: "Avg 7D",
    cell: ({ row }) => {
      const val = row.getValue<number>("avg_7d");
      return <span className={cn(percentColorClass(val))}>{formatPercent(val)}</span>;
    },
  },
  {
    accessorKey: "avg_30d",
    header: "Avg 30D",
    cell: ({ row }) => {
      const val = row.getValue<number>("avg_30d");
      return <span className={cn(percentColorClass(val))}>{formatPercent(val)}</span>;
    },
  },
];

export function TrackingTable({ data }: TrackingTableProps) {
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
              <TableRow key={row.id}>
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
                No data available.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
