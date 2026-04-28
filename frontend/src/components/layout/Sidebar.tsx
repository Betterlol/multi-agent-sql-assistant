import { Database, Table2 } from "lucide-react";

import type { TableSchema, UploadResponse } from "../../lib/types";
import { Card } from "../ui/Card";

interface SidebarProps {
  tableSchema: TableSchema;
  tableCount: number;
  uploadInfo: UploadResponse | null;
}

export function Sidebar({ tableSchema, tableCount, uploadInfo }: SidebarProps) {
  const tableEntries = Object.entries(tableSchema);

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-900 dark:text-zinc-100">
          <Database className="h-4 w-4 text-zinc-700 dark:text-zinc-300" />
          Database Context
        </div>
        {uploadInfo ? (
          <div className="mt-3 space-y-2 text-xs text-zinc-600 dark:text-zinc-300">
            <p>
              <span className="font-semibold text-zinc-800 dark:text-zinc-200">File:</span> {uploadInfo.filename}
            </p>
            <p>
              <span className="font-semibold text-zinc-800 dark:text-zinc-200">Database ID:</span>
            </p>
            <p className="break-all rounded-lg bg-zinc-100 px-2 py-1 font-mono text-[11px] dark:bg-zinc-800/80">{uploadInfo.database_id}</p>
          </div>
        ) : (
          <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-400">Upload a SQLite file to inspect schema.</p>
        )}
      </Card>

      <Card className="p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Schema Explorer</h2>
          <span className="rounded-full bg-zinc-100 px-2 py-1 text-[11px] font-semibold text-zinc-600 dark:bg-zinc-800/70 dark:text-zinc-300">
            {tableCount} tables
          </span>
        </div>

        {tableEntries.length === 0 ? (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">No schema loaded.</p>
        ) : (
          <div className="max-h-[58vh] space-y-2 overflow-auto pr-1">
            {tableEntries.map(([table, columns]) => (
              <details key={table} className="group rounded-xl border border-zinc-200 bg-white/85 dark:border-zinc-700/60 dark:bg-zinc-900/70" open>
                <summary className="flex cursor-pointer items-center gap-2 px-3 py-2 text-sm font-semibold text-zinc-800 marker:content-none dark:text-zinc-100">
                  <Table2 className="h-4 w-4 text-zinc-500 dark:text-zinc-400" />
                  <span className="truncate">{table}</span>
                  <span className="ml-auto text-xs font-medium text-zinc-400 dark:text-zinc-500">{columns.length}</span>
                </summary>
                <ul className="space-y-1 border-t border-zinc-100 px-3 py-2 dark:border-zinc-700/60">
                  {columns.map((column) => (
                    <li
                      key={column}
                      className="truncate rounded-md px-1.5 py-1 font-mono text-xs text-zinc-600 hover:bg-zinc-50 dark:text-zinc-300 dark:hover:bg-zinc-800/70"
                    >
                      {column}
                    </li>
                  ))}
                </ul>
              </details>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
