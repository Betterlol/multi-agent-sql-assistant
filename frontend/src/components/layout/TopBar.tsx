import { Activity, CloudOff, Database, Gauge, Sparkles, Upload } from "lucide-react";

import type { MetricsResponse, UploadResponse } from "../../lib/types";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Spinner } from "../ui/Spinner";

interface TopBarProps {
  metrics: MetricsResponse | null;
  backendOk: boolean;
  file: File | null;
  uploading: boolean;
  uploadInfo: UploadResponse | null;
  onFileChange: (file: File | null) => void;
  onUpload: () => void;
}

export function TopBar({
  metrics,
  backendOk,
  file,
  uploading,
  uploadInfo,
  onFileChange,
  onUpload,
}: TopBarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div className="min-w-0">
        <div className="inline-flex items-center gap-2 rounded-xl border border-zinc-200 bg-white px-3 py-1 text-xs font-semibold text-zinc-600">
          <Sparkles className="h-3.5 w-3.5" />
          AI SQL Workbench
        </div>
        <h1 className="mt-2 text-lg font-bold tracking-tight text-zinc-900 md:text-xl">SQL Assistant</h1>
        <p className="text-sm text-zinc-500">FastAPI + SQLite + QuerySpec + Parameterized SQL</p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <label className="inline-flex h-10 cursor-pointer items-center rounded-xl border border-zinc-200 bg-white px-3.5 text-sm font-semibold text-zinc-700 shadow-sm transition hover:bg-zinc-50">
          <Upload className="mr-2 h-4 w-4" />
          {file ? file.name : "Choose SQLite"}
          <input
            type="file"
            accept=".sqlite,.sqlite3,.db"
            className="hidden"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
          />
        </label>

        <Button onClick={onUpload} disabled={!file || uploading}>
          {uploading ? (
            <span className="inline-flex items-center gap-2">
              <Spinner />
              Uploading
            </span>
          ) : (
            "Upload"
          )}
        </Button>

        {backendOk ? (
          <Badge tone="success">Backend Online</Badge>
        ) : (
          <Badge tone="danger" className="inline-flex items-center gap-1">
            <CloudOff className="h-3 w-3" />
            Backend Offline
          </Badge>
        )}

        <Badge className="inline-flex items-center gap-1">
          <Database className="h-3 w-3" />
          Tables: {uploadInfo?.table_count ?? 0}
        </Badge>
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
