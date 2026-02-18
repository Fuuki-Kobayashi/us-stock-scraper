"use client";

import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/stores/uiStore";

export function Header() {
  const setSearchOpen = useUIStore((s) => s.setSearchOpen);

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
      <h2 className="text-sm font-medium text-muted-foreground">
        US Stock Surge Analyzer
      </h2>
      <Button
        variant="outline"
        size="sm"
        className="gap-2 text-muted-foreground"
        onClick={() => setSearchOpen(true)}
      >
        <Search className="h-4 w-4" />
        <span className="hidden sm:inline">Search...</span>
        <kbd className="pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium sm:flex">
          <span className="text-xs">&#8984;</span>K
        </kbd>
      </Button>
    </header>
  );
}
