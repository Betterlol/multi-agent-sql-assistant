import { Card } from "../ui/Card";

interface VerifiedSQLPanelProps {
  sql?: string | null;
}

export function VerifiedSQLPanel({ sql }: VerifiedSQLPanelProps) {
  return (
    <Card>
      <pre className="whitespace-pre-wrap break-words font-mono text-xs text-slate-200">{sql || "-"}</pre>
    </Card>
  );
}
