import type { HTMLAttributes } from "react";

import { cn } from "../../lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "default" | "success" | "warning" | "danger";
}

export function Badge({ className, tone = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
        tone === "default" && "bg-slate-800 text-slate-200",
        tone === "success" && "bg-emerald-900/40 text-emerald-300",
        tone === "warning" && "bg-amber-900/40 text-amber-300",
        tone === "danger" && "bg-rose-900/40 text-rose-300",
        className
      )}
      {...props}
    />
  );
}
