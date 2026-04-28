import { Clock3 } from "lucide-react";

import type { HistoryItem } from "../../lib/types";
import { formatTime } from "../../lib/utils";
import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";

interface QueryHistoryProps {
  items: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
}

export function QueryHistory({ items, onSelect }: QueryHistoryProps) {
  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-900 dark:text-zinc-100">
        <Clock3 className="h-4 w-4 text-zinc-500 dark:text-zinc-400" />
        Query History
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-400">No history yet.</p>
      ) : (
        <div className="max-h-[28vh] space-y-2 overflow-auto pr-1">
          {items.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onSelect(item)}
              className="w-full rounded-xl border border-zinc-200 bg-white/90 p-3 text-left transition hover:border-zinc-300 hover:bg-zinc-50 dark:border-zinc-700/60 dark:bg-zinc-900/70 dark:hover:border-zinc-600 dark:hover:bg-zinc-800/70"
            >
              <p className="line-clamp-2 text-sm text-zinc-700 dark:text-zinc-200">{item.question}</p>
              <div className="mt-2 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
                <span>{formatTime(item.timestamp)}</span>
                <Badge tone={item.success ? "success" : "danger"}>{item.success ? "success" : "failed"}</Badge>
              </div>
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}
