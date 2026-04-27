import { Activity, CloudOff, Gauge } from "lucide-react";

import type { MetricsResponse } from "../../lib/types";
import { Badge } from "../ui/Badge";

interface TopBarProps {
  metrics: MetricsResponse | null;
  backendOk: boolean;
}

export function TopBar({ metrics, backendOk }: TopBarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 className="text-lg font-semibold">SQL Assistant Workbench</h1>
        <p className="text-xs text-slate-400">FastAPI + SQLite + QuerySpec + Parameterized SQL</p>
      </div>

      <div className="flex items-center gap-2 text-xs">
        {backendOk ? (
          <Badge tone="success">Backend Online</Badge>
        ) : (
          <Badge tone="danger" className="inline-flex items-center gap-1">
            <CloudOff className="h-3 w-3" />
            Backend Offline
          </Badge>
        )}
        <Badge className="inline-flex items-center gap-1">
          <Activity className="h-3 w-3" />
          Queries: {metrics?.queries_total ?? 0}
        </Badge>
        <Badge className="inline-flex items-center gap-1">
          <Gauge className="h-3 w-3" />
          P95: {metrics?.latency_ms?.p95 ?? 0} ms
        </Badge>
      </div>
    </div>
  );
}
