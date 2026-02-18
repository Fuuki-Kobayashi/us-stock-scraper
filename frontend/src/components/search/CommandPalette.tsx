"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import { useUIStore } from "@/stores/uiStore";
import { useSearch } from "@/hooks/useSearch";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Search } from "lucide-react";

export function CommandPalette() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const searchOpen = useUIStore((s) => s.searchOpen);
  const setSearchOpen = useUIStore((s) => s.setSearchOpen);
  const { data: results } = useSearch(query);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setSearchOpen(!searchOpen);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [searchOpen, setSearchOpen]);

  const handleSelect = (symbol: string) => {
    setSearchOpen(false);
    setQuery("");
    router.push(`/stocks/${symbol}`);
  };

  return (
    <Dialog open={searchOpen} onOpenChange={setSearchOpen}>
      <DialogContent className="overflow-hidden p-0 max-w-lg">
        <Command className="rounded-lg border-none" shouldFilter={false}>
          <div className="flex items-center border-b px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            <Command.Input
              value={query}
              onValueChange={setQuery}
              placeholder="Search ticker or company name..."
              className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground"
            />
          </div>
          <Command.List className="max-h-[300px] overflow-y-auto p-2">
            {query.length > 0 && (!results || results.length === 0) && (
              <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
                No results found.
              </Command.Empty>
            )}
            {results?.map((result) => (
              <Command.Item
                key={result.symbol}
                value={result.symbol}
                onSelect={() => handleSelect(result.symbol)}
                className="flex items-center justify-between rounded-md px-3 py-2 text-sm cursor-pointer hover:bg-accent"
              >
                <div>
                  <span className="font-medium">{result.symbol}</span>
                  <span className="ml-2 text-muted-foreground">
                    {result.name}
                  </span>
                </div>
                {result.exchange && (
                  <span className="text-xs text-muted-foreground">
                    {result.exchange}
                  </span>
                )}
              </Command.Item>
            ))}
          </Command.List>
        </Command>
      </DialogContent>
    </Dialog>
  );
}
