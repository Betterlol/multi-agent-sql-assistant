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
    <Card>
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-200">
        <Clock3 className="h-4 w-4 text-cyan-400" />
        Query History
      </div>

      {items.length === 0 ? (
        <p className="text-xs text-slate-500">暂无历史记录</p>
      ) : (
        <div className="max-h-56 space-y-2 overflow-auto">
          {items.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onSelect(item)}
              className="w-full rounded-md border border-slate-800 bg-slate-950/60 p-2 text-left hover:bg-slate-900"
            >
              <div className="line-clamp-2 text-xs text-slate-200">{item.question}</div>
              <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
                <span>{formatTime(item.timestamp)}</span>
                <Badge tone={item.success ? "success" : "danger"}>{item.success ? "ok" : "fail"}</Badge>
              </div>
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}
