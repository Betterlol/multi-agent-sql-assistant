import { Card } from "../ui/Card";

interface WarningsPanelProps {
  warnings: string[];
  specWarnings: string[];
}

export function WarningsPanel({ warnings, specWarnings }: WarningsPanelProps) {
  const all = [...warnings, ...specWarnings];
  return (
    <Card>
      {all.length === 0 ? (
        <p className="text-xs text-slate-500">无 warnings</p>
      ) : (
        <ul className="space-y-2 text-xs text-amber-300">
          {all.map((warning, index) => (
            <li key={`${warning}-${index}`}>- {warning}</li>
          ))}
        </ul>
      )}
    </Card>
  );
}
