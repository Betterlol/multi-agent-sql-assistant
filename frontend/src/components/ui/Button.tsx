import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "../../lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "primary" | "secondary" | "danger";
}

export function Button({ children, className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
        "focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-slate-950",
        variant === "primary" && "bg-cyan-500 text-slate-950 hover:bg-cyan-400 disabled:bg-cyan-800",
        variant === "secondary" && "bg-slate-800 text-slate-100 hover:bg-slate-700 disabled:bg-slate-900",
        variant === "danger" && "bg-rose-600 text-white hover:bg-rose-500 disabled:bg-rose-900",
        "disabled:cursor-not-allowed",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
