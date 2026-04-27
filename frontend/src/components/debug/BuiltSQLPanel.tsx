import { Card } from "../ui/Card";

interface BuiltSQLPanelProps {
  sql?: string | null;
}

export function BuiltSQLPanel({ sql }: BuiltSQLPanelProps) {
  return (
    <Card>
      <pre className="whitespace-pre-wrap break-words font-mono text-xs text-slate-200">{sql || "-"}</pre>
    </Card>
  );
}
