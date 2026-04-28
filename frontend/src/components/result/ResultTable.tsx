import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { DatabaseZap } from "lucide-react";
import { useMemo } from "react";

import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";

interface ResultTableProps {
  columns: string[];
  rows: Array<Array<string | number | boolean | null>>;
}

export function ResultTable({ columns, rows }: ResultTableProps) {
  const data = useMemo(
    () =>
      rows.map((row) => {
        const record: Record<string, string | number | boolean | null> = {};
        columns.forEach((column, index) => {
          record[column] = row[index] ?? null;
        });
        return record;
      }),
    [columns, rows]
  );

  const tableColumns = useMemo<ColumnDef<Record<string, string | number | boolean | null>>[]>(
    () =>
      columns.map((column) => ({
        accessorKey: column,
        header: column,
        cell: ({ getValue }) => {
          const value = getValue<string | number | boolean | null>();
          if (value === null) {
            return <Badge tone="warning">NULL</Badge>;
          }
          return <span className="font-mono text-xs text-zinc-700 dark:text-zinc-200">{String(value)}</span>;
        },
      })),
    [columns]
  );

  const table = useReactTable({
    data,
    columns: tableColumns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  });

  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Result Table</h3>
        <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">{rows.length} rows</span>
      </div>

      {columns.length === 0 ? (
        <div className="flex min-h-[220px] flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-300 bg-zinc-50 text-center dark:border-zinc-700/70 dark:bg-zinc-900/60">
          <DatabaseZap className="mb-3 h-6 w-6 text-zinc-400 dark:text-zinc-500" />
          <p className="text-sm font-medium text-zinc-700 dark:text-zinc-200">No rows returned</p>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">Try broadening your query or increasing max rows.</p>
        </div>
      ) : (
        <>
          <div className="max-w-full overflow-auto rounded-2xl border border-zinc-200 dark:border-zinc-700/70">
            <table className="min-w-full text-left text-xs">
              <thead className="sticky top-0 z-10 bg-zinc-100/95 backdrop-blur dark:bg-zinc-800/85">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="border-b border-zinc-200 px-3 py-2.5 text-xs font-semibold text-zinc-700 dark:border-zinc-700/70 dark:text-zinc-200"
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b border-zinc-100 odd:bg-white even:bg-zinc-50/50 hover:bg-indigo-50/40 dark:border-zinc-800/70 dark:odd:bg-zinc-900/50 dark:even:bg-zinc-800/45 dark:hover:bg-indigo-500/12"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-3 py-2.5 align-top">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-end gap-2">
            <Button variant="secondary" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
              Prev
            </Button>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">
              Page {table.getState().pagination.pageIndex + 1} / {table.getPageCount() || 1}
            </span>
            <Button variant="secondary" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
              Next
            </Button>
          </div>
        </>
      )}
    </Card>
  );
}
