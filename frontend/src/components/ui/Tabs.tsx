import { useMemo, useState, type ReactNode } from "react";

import { cn } from "../../lib/utils";

export interface TabItem {
  key: string;
  label: string;
  content: ReactNode;
}

interface TabsProps {
  items: TabItem[];
  defaultKey?: string;
}

export function Tabs({ items, defaultKey }: TabsProps) {
  const initial = useMemo(() => defaultKey ?? items[0]?.key ?? "", [defaultKey, items]);
  const [active, setActive] = useState(initial);

  const activeItem = items.find((item) => item.key === active) ?? items[0];

  return (
    <div className="flex h-full min-h-0 flex-col gap-4">
      <div className="overflow-x-auto">
        <div className="inline-flex rounded-xl border border-zinc-200 bg-zinc-100/80 p-1 dark:border-zinc-700 dark:bg-zinc-800/70">
          {items.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => setActive(item.key)}
              className={cn(
                "rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors",
                item.key === active
                  ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-900 dark:text-zinc-100"
                  : "text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-100"
              )}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <div className="min-h-0 flex-1">{activeItem?.content}</div>
    </div>
  );
}
