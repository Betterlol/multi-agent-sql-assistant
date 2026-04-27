import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
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
          return <span className="font-mono text-xs text-slate-200">{String(value)}</span>;
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
    <Card>
      <div className="mb-3 flex items-center justify-between">
        <div className="text-sm font-semibold text-slate-200">Result Rows</div>
        <div className="text-xs text-slate-500">{rows.length} rows</div>
      </div>

      {columns.length === 0 ? (
        <div className="rounded-md border border-dashed border-slate-700 p-6 text-center text-sm text-slate-500">
          暂无结果
        </div>
      ) : (
        <>
          <div className="max-w-full overflow-auto rounded-md border border-slate-800">
            <table className="min-w-full text-left text-xs">
              <thead className="sticky top-0 bg-slate-900">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th key={header.id} className="border-b border-slate-800 px-3 py-2 font-semibold text-slate-300">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="border-b border-slate-900/60">
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-3 py-2 align-top">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-3 flex items-center justify-end gap-2">
            <Button
              variant="secondary"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Prev
            </Button>
            <span className="text-xs text-slate-400">
              Page {table.getState().pagination.pageIndex + 1} / {table.getPageCount() || 1}
            </span>
            <Button
              variant="secondary"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </Button>
          </div>
        </>
      )}
    </Card>
  );
}
