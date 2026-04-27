import type { ReactNode } from "react";

interface AppLayoutProps {
  sidebar: ReactNode;
  topbar: ReactNode;
  children: ReactNode;
}

export function AppLayout({ sidebar, topbar, children }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside className="border-r border-slate-800 bg-slate-950/90 p-4">{sidebar}</aside>
        <main className="flex min-h-screen flex-col">
          <div className="border-b border-slate-800 p-4">{topbar}</div>
          <div className="flex-1 overflow-auto p-4">{children}</div>
        </main>
      </div>
    </div>
  );
}
