import type { ReactNode } from "react";

import { theme } from "../../styles/theme";

interface AppLayoutProps {
  sidebar: ReactNode;
  header: ReactNode;
  inspector: ReactNode;
  children: ReactNode;
}

export function AppLayout({ sidebar, header, inspector, children }: AppLayoutProps) {
  return (
    <div className={`min-h-screen ${theme.colors.background}`}>
      <header className="sticky top-0 z-40 border-b border-zinc-200/80 bg-white/85 backdrop-blur">
        <div className="mx-auto max-w-[1700px] px-4 py-3 md:px-6">{header}</div>
      </header>

      <div className="mx-auto grid max-w-[1700px] grid-cols-1 gap-6 p-4 md:p-6 xl:grid-cols-[280px_minmax(0,1fr)_420px]">
        <aside className="space-y-6 xl:sticky xl:top-[84px] xl:max-h-[calc(100vh-104px)] xl:overflow-y-auto">{sidebar}</aside>
        <main className="space-y-6 min-w-0">{children}</main>
        <section className="min-w-0 xl:sticky xl:top-[84px] xl:h-[calc(100vh-104px)] xl:overflow-hidden">{inspector}</section>
      </div>
    </div>
  );
}
