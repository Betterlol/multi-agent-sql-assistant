import type { HTMLAttributes } from "react";

import { cn } from "../../lib/utils";
import { theme } from "../../styles/theme";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl border p-5 shadow-sm transition-colors",
        theme.colors.surface,
        theme.colors.border,
        className
      )}
      {...props}
    />
  );
}
