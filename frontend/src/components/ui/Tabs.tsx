import { useMemo, useState } from "react";

import { cn } from "../../lib/utils";

export interface TabItem {
  key: string;
  label: string;
  content: React.ReactNode;
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
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {items.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setActive(item.key)}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-medium",
              item.key === active
                ? "bg-cyan-500 text-slate-950"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div>{activeItem?.content}</div>
    </div>
  );
}
