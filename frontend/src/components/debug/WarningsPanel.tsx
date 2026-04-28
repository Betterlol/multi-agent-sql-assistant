import { AlertTriangle } from "lucide-react";

interface WarningsPanelProps {
  warnings: string[];
  specWarnings: string[];
}

export function WarningsPanel({ warnings, specWarnings }: WarningsPanelProps) {
  const all = [...warnings, ...specWarnings];

  return (
    <div className="flex h-full min-h-0 flex-col rounded-2xl border border-zinc-200 bg-white dark:border-zinc-700/70 dark:bg-zinc-900/70">
      <div className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-700/70">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Warnings</h3>
      </div>
      <div className="min-h-0 flex-1 overflow-auto p-4">
        {all.length === 0 ? (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">No warnings.</p>
        ) : (
          <ul className="space-y-2">
            {all.map((warning, index) => (
              <li
                key={`${warning}-${index}`}
                className="inline-flex w-full items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-500/35 dark:bg-amber-500/14 dark:text-amber-200"
              >
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                <span>{warning}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
