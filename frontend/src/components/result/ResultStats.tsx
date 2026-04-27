import { Activity, Database, Rows2, Timer } from "lucide-react";

import { Badge } from "../ui/Badge";

interface ResultStatsProps {
  rowCount: number;
  selectedTable: string;
  intent: string;
  latencyMs: number | null;
}

export function ResultStats({ rowCount, selectedTable, intent, latencyMs }: ResultStatsProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge className="inline-flex items-center gap-1.5">
        <Rows2 className="h-3 w-3" />
        Rows: {rowCount}
      </Badge>
      <Badge className="inline-flex items-center gap-1.5">
        <Database className="h-3 w-3" />
        Table: {selectedTable || "-"}
      </Badge>
      <Badge tone="accent" className="inline-flex items-center gap-1.5">
        <Activity className="h-3 w-3" />
        Mode: {intent || "-"}
      </Badge>
      <Badge className="inline-flex items-center gap-1.5">
        <Timer className="h-3 w-3" />
        Latency: {latencyMs === null ? "-" : `${latencyMs} ms`}
      </Badge>
    </div>
  );
}
