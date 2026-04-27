import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "../../lib/utils";
import { theme } from "../../styles/theme";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "primary" | "secondary" | "danger" | "ghost";
}

export function Button({ children, className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-xl border px-4 text-sm font-semibold transition-all duration-150",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300",
        "disabled:cursor-not-allowed disabled:opacity-55",
        variant === "primary" && cn("border-zinc-900", theme.colors.primary),
        variant === "secondary" && cn("border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50"),
        variant === "danger" && cn("border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100"),
        variant === "ghost" && cn("border-transparent bg-transparent text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"),
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
