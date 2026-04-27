import { Card } from "../ui/Card";

interface ParamsPanelProps {
  params?: unknown[] | null;
}

export function ParamsPanel({ params }: ParamsPanelProps) {
  return (
    <Card>
      <pre className="whitespace-pre-wrap break-words font-mono text-xs text-slate-200">
        {JSON.stringify(params ?? [], null, 2)}
      </pre>
    </Card>
  );
}
