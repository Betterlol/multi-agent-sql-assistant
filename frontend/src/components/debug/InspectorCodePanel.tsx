import { Check, Copy } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "../ui/Button";

interface InspectorCodePanelProps {
  title: string;
  content: string;
  emptyText?: string;
  language?: "json" | "sql" | "text";
}

function formatContent(content: string, language: "json" | "sql" | "text") {
  if (!content.trim()) {
    return "";
  }
  if (language === "json") {
    try {
      return JSON.stringify(JSON.parse(content), null, 2);
    } catch {
      return content;
    }
  }
  if (language === "sql") {
    return content
      .replace(/\s+/g, " ")
      .replace(/\b(SELECT|FROM|WHERE|ORDER BY|GROUP BY|LIMIT|OFFSET|AND|OR|COUNT)\b/gi, "\n$1")
      .trim();
  }
  return content;
}

export function InspectorCodePanel({
  title,
  content,
  emptyText = "No content",
  language = "text",
}: InspectorCodePanelProps) {
  const [copied, setCopied] = useState(false);
  const formatted = useMemo(() => formatContent(content, language), [content, language]);

  const handleCopy = async () => {
    if (!formatted) {
      return;
    }
    try {
      await navigator.clipboard.writeText(formatted);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col rounded-2xl border border-zinc-800 bg-zinc-900">
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-400">{title}</h3>
        <Button variant="ghost" onClick={handleCopy} className="h-8 border border-zinc-700 bg-zinc-800 text-zinc-200 hover:bg-zinc-700">
          {copied ? (
            <span className="inline-flex items-center gap-1.5 text-xs">
              <Check className="h-3.5 w-3.5" />
              Copied
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 text-xs">
              <Copy className="h-3.5 w-3.5" />
              Copy
            </span>
          )}
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-auto p-4">
        {formatted ? (
          <pre className="whitespace-pre-wrap break-words font-mono text-xs leading-6 text-zinc-100">{formatted}</pre>
        ) : (
          <p className="text-sm text-zinc-500">{emptyText}</p>
        )}
      </div>
    </div>
  );
}
