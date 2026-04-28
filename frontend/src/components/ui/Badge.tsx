import type { HTMLAttributes } from "react";

import { cn } from "../../lib/utils";
import { theme } from "../../styles/theme";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "default" | "success" | "warning" | "danger" | "accent";
}

export function Badge({ className, tone = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold leading-none",
        tone === "default" && "border-zinc-200 bg-zinc-100 text-zinc-700 dark:border-zinc-700/70 dark:bg-zinc-800/70 dark:text-zinc-200",
        tone === "success" && theme.colors.success,
        tone === "warning" && theme.colors.warning,
        tone === "danger" && theme.colors.danger,
        tone === "accent" && theme.colors.accent,
        className
      )}
      {...props}
    />
  );
}
