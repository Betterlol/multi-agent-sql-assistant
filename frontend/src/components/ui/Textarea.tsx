import type { TextareaHTMLAttributes } from "react";

import { cn } from "../../lib/utils";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-32 w-full rounded-2xl border border-zinc-200 bg-white px-4 py-3.5 text-sm text-zinc-900 shadow-sm",
        "placeholder:text-zinc-400 focus:border-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-100",
        className
      )}
      {...props}
    />
  );
}
