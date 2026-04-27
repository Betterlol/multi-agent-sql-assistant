import type { InputHTMLAttributes } from "react";

import { cn } from "../../lib/utils";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-9 w-full rounded-md border border-slate-700 bg-slate-950 px-3 text-sm text-slate-100",
        "placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none"
      )}
      {...props}
    />
  );
}
