import { Upload } from "lucide-react";

import type { UploadResponse } from "../../lib/types";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Input } from "../ui/Input";
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
    <Card>
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-200">
        <Upload className="h-4 w-4 text-cyan-400" />
        Database Upload
      </div>
      <div className="space-y-3">
        <Input
          type="file"
          accept=".sqlite,.sqlite3,.db"
          onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        />
        <Button onClick={onUpload} disabled={!file || uploading} className="w-full">
          {uploading ? (
            <span className="inline-flex items-center gap-2">
              <Spinner />
              Uploading...
            </span>
          ) : (
            "Upload SQLite"
          )}
        </Button>
      </div>

      <div className="mt-3 text-xs text-slate-400">
        {uploadInfo ? (
          <div className="space-y-1">
            <p>File: {uploadInfo.filename}</p>
            <p>Table Count: {uploadInfo.table_count}</p>
            <p>Database ID: <span className="font-mono text-slate-200">{uploadInfo.database_id}</span></p>
          </div>
        ) : (
          "支持 .sqlite / .sqlite3 / .db"
        )}
      </div>
    </Card>
  );
}
