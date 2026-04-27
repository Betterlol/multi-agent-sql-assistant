import type { TextareaHTMLAttributes } from "react";

import { cn } from "../../lib/utils";

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-24 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100",
        "placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none"
      )}
      {...props}
    />
  );
}
