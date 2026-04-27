import { Database, Upload } from "lucide-react";

import type { UploadResponse } from "../../lib/types";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Spinner } from "../ui/Spinner";

interface UploadPanelProps {
  file: File | null;
  uploading: boolean;
  uploadInfo: UploadResponse | null;
  onFileChange: (file: File | null) => void;
  onUpload: () => void;
}

export function UploadPanel({ file, uploading, uploadInfo, onFileChange, onUpload }: UploadPanelProps) {
  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-900">
        <Upload className="h-4 w-4 text-zinc-500" />
        Database Upload
      </div>

      <div className="space-y-3">
        <label className="inline-flex h-11 w-full cursor-pointer items-center rounded-xl border border-zinc-200 bg-white px-3 text-sm font-semibold text-zinc-600 transition hover:bg-zinc-50">
          {file ? file.name : "Choose .sqlite/.db file"}
          <input
            type="file"
            accept=".sqlite,.sqlite3,.db"
            className="hidden"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
          />
        </label>
        <Button onClick={onUpload} disabled={!file || uploading} className="w-full">
          {uploading ? (
            <span className="inline-flex items-center gap-2">
              <Spinner />
              Uploading
            </span>
          ) : (
            "Upload SQLite"
          )}
        </Button>
      </div>

      <div className="mt-3 rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-xs text-zinc-600">
        {uploadInfo ? (
          <div className="space-y-1">
            <p className="inline-flex items-center gap-1.5">
              <Database className="h-3.5 w-3.5" />
              <span className="font-semibold">{uploadInfo.table_count}</span> tables loaded
            </p>
            <p className="break-all font-mono text-[11px]">{uploadInfo.database_id}</p>
          </div>
        ) : (
          "Supports .sqlite / .sqlite3 / .db"
        )}
      </div>
    </Card>
  );
}
