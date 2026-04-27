import { Database, Table2 } from "lucide-react";

import type { TableSchema } from "../../lib/types";
import { Card } from "../ui/Card";

interface SidebarProps {
  tableSchema: TableSchema;
  tableCount: number;
}

export function Sidebar({ tableSchema, tableCount }: SidebarProps) {
  const tableEntries = Object.entries(tableSchema);

  return (
    <div className="space-y-4">
      <Card>
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          <Database className="h-4 w-4 text-cyan-400" />
          Schema Viewer
        </div>
        <p className="mt-2 text-xs text-slate-400">Tables: {tableCount}</p>
      </Card>

      <Card className="max-h-[70vh] overflow-auto">
        <div className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-400">Tables</div>
        {tableEntries.length === 0 ? (
          <p className="text-sm text-slate-500">上传数据库后显示表结构</p>
        ) : (
          <div className="space-y-3">
            {tableEntries.map(([table, columns]) => (
              <div key={table} className="rounded-md border border-slate-800 bg-slate-950/60 p-2">
                <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-100">
                  <Table2 className="h-4 w-4 text-cyan-500" />
                  {table}
                </div>
                <ul className="space-y-1 pl-1 text-xs text-slate-300">
                  {columns.map((column) => (
                    <li key={column} className="font-mono">- {column}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
