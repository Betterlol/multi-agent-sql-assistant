export const theme = {
  colors: {
    background: "bg-transparent text-zinc-900 dark:text-zinc-100",
    surface:
      "bg-white/60 backdrop-blur-xl border border-white/25 shadow-[0_12px_40px_rgba(15,23,42,0.08)] dark:bg-zinc-900/55 dark:backdrop-blur-xl dark:border-zinc-700/45 dark:shadow-[0_18px_60px_rgba(2,6,23,0.55)]",
    surfaceHover: "hover:bg-white/80 dark:hover:bg-zinc-800/60 transition-colors",
    border: "border-zinc-200/50 dark:border-zinc-700/45",
    muted: "bg-zinc-100/60 dark:bg-zinc-800/55",
    text: "text-zinc-900 dark:text-zinc-100",
    textSecondary: "text-zinc-500 dark:text-zinc-400",
    primary:
      "bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 shadow-lg shadow-zinc-500/10 dark:shadow-black/35",
    accent: "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-500/20 dark:text-indigo-200 dark:border-indigo-500/30",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/20 dark:text-emerald-200 dark:border-emerald-500/30",
    warning: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/20 dark:text-amber-200 dark:border-amber-500/30",
    danger: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-500/20 dark:text-rose-200 dark:border-rose-500/30",
    codeBackground: "bg-zinc-900 text-zinc-100 border-zinc-800",
  },
} as const;
