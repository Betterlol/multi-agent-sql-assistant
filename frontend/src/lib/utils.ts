import clsx from "clsx";

import type { HistoryItem } from "./types";

const QUERY_HISTORY_KEY = "sql-assistant-query-history";

export function cn(...inputs: Array<string | false | null | undefined>): string {
  return clsx(inputs);
}

export function formatTime(ts: number): string {
  return new Date(ts).toLocaleString("zh-CN", {
    hour12: false,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function loadHistory(): HistoryItem[] {
  try {
    const raw = localStorage.getItem(QUERY_HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as HistoryItem[];
    if (!Array.isArray(parsed)) return [];
    return parsed;
  } catch {
    return [];
  }
}

export function saveHistory(items: HistoryItem[]): void {
  localStorage.setItem(QUERY_HISTORY_KEY, JSON.stringify(items.slice(0, 30)));
}
