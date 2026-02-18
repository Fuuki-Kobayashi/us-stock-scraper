"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSettings, useUpdateSettings } from "@/hooks/useSettings";

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings();
  const updateSettings = useUpdateSettings();
  const [threshold, setThreshold] = useState<number>(20);

  useEffect(() => {
    if (settings) {
      setThreshold(settings.surge_threshold);
    }
  }, [settings]);

  const handleSave = () => {
    updateSettings.mutate({ surge_threshold: threshold });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <Card className="max-w-md">
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Surge Detection Threshold
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading settings...</p>
          ) : (
            <>
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">
                  Minimum daily change percentage to qualify as a surge
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                    min={1}
                    max={100}
                    step={1}
                    className="w-24"
                  />
                  <span className="text-sm text-muted-foreground">%</span>
                </div>
              </div>
              <Button
                onClick={handleSave}
                disabled={updateSettings.isPending}
              >
                {updateSettings.isPending ? "Saving..." : "Save"}
              </Button>
              {updateSettings.isSuccess && (
                <p className="text-sm text-emerald-500">Settings saved.</p>
              )}
              {updateSettings.isError && (
                <p className="text-sm text-red-500">
                  Failed to save settings. Please try again.
                </p>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
