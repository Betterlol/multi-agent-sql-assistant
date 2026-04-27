import { Card } from "../ui/Card";

interface QuerySpecPanelProps {
  value: unknown;
}

export function QuerySpecPanel({ value }: QuerySpecPanelProps) {
  return (
    <Card>
      <pre className="whitespace-pre-wrap break-words font-mono text-xs text-slate-200">
        {value ? JSON.stringify(value, null, 2) : "-"}
      </pre>
    </Card>
  );
}
