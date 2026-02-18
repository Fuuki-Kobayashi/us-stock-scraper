"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAdminStatus, useCollect, useBackfill } from "@/hooks/useAdmin";
import { formatDateTime } from "@/lib/formatters";

export default function AdminPage() {
  const { data: status, isLoading } = useAdminStatus();
  const collect = useCollect();
  const backfill = useBackfill();
  const [collectDate, setCollectDate] = useState("");
  const [backfillFrom, setBackfillFrom] = useState("");
  const [backfillTo, setBackfillTo] = useState("");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Scheduler Status</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : status ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Status:</span>
                <Badge variant={status.scheduler_running ? "default" : "secondary"}>
                  {status.scheduler_running ? "Running" : "Stopped"}
                </Badge>
              </div>
              {status.next_run && (
                <div className="text-sm">
                  <span className="text-muted-foreground">Next run: </span>
                  {formatDateTime(status.next_run)}
                </div>
              )}
              {status.last_run && (
                <div className="text-sm">
                  <span className="text-muted-foreground">Last run: </span>
                  {formatDateTime(status.last_run)}
                  {status.last_run_status && (
                    <Badge variant="outline" className="ml-2">
                      {status.last_run_status}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Unable to fetch status.</p>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Manual Collection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">
                Date (leave empty for today)
              </label>
              <Input
                type="date"
                value={collectDate}
                onChange={(e) => setCollectDate(e.target.value)}
                className="w-48"
              />
            </div>
            <Button
              onClick={() => collect.mutate(collectDate || undefined)}
              disabled={collect.isPending}
            >
              {collect.isPending ? "Collecting..." : "Run Collection"}
            </Button>
            {collect.isSuccess && (
              <p className="text-sm text-emerald-500">Collection completed.</p>
            )}
            {collect.isError && (
              <p className="text-sm text-red-500">Collection failed.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Backfill</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">From Date</label>
                <Input
                  type="date"
                  value={backfillFrom}
                  onChange={(e) => setBackfillFrom(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">To Date</label>
                <Input
                  type="date"
                  value={backfillTo}
                  onChange={(e) => setBackfillTo(e.target.value)}
                />
              </div>
            </div>
            <Button
              onClick={() =>
                backfill.mutate({
                  from_date: backfillFrom,
                  to_date: backfillTo,
                })
              }
              disabled={
                backfill.isPending || !backfillFrom || !backfillTo
              }
            >
              {backfill.isPending ? "Running..." : "Run Backfill"}
            </Button>
            {backfill.isSuccess && (
              <p className="text-sm text-emerald-500">Backfill completed.</p>
            )}
            {backfill.isError && (
              <p className="text-sm text-red-500">Backfill failed.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
