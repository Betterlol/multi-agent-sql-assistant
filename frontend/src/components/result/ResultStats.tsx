import { Card } from "../ui/Card";

interface ResultStatsProps {
  rowCount: number;
  selectedTable: string;
  intent: string;
  latencyMs: number | null;
}

export function ResultStats({ rowCount, selectedTable, intent, latencyMs }: ResultStatsProps) {
  const stats = [
    { label: "Row Count", value: String(rowCount) },
    { label: "Selected Table", value: selectedTable || "-" },
    { label: "Intent", value: intent || "-" },
    { label: "Latency", value: latencyMs === null ? "-" : `${latencyMs} ms` },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {stats.map((item) => (
        <Card key={item.label} className="p-3">
          <div className="text-xs text-slate-400">{item.label}</div>
          <div className="mt-1 font-mono text-sm text-slate-100">{item.value}</div>
        </Card>
      ))}
    </div>
  );
}
