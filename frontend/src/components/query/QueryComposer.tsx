import { Play, Sparkles } from "lucide-react";

import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Input } from "../ui/Input";
import { Spinner } from "../ui/Spinner";
import { Textarea } from "../ui/Textarea";

interface QueryComposerProps {
  question: string;
  maxRows: number;
  llmEnabled: boolean;
  apiKey: string;
  model: string;
  baseUrl: string;
  running: boolean;
  canRun: boolean;
  onQuestionChange: (value: string) => void;
  onMaxRowsChange: (value: number) => void;
  onLLMEnabledChange: (value: boolean) => void;
  onApiKeyChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onBaseUrlChange: (value: string) => void;
  onRun: () => void;
}

export function QueryComposer(props: QueryComposerProps) {
  return (
    <Card className="space-y-5 p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-zinc-900">Query Composer</h2>
          <p className="mt-1 text-sm text-zinc-500">Describe the result you need. The assistant will build safe SQL.</p>
        </div>
        <Badge tone="accent" className="inline-flex items-center gap-1">
          <Sparkles className="h-3 w-3" />
          AI Native
        </Badge>
      </div>

      <Textarea
        value={props.question}
        onChange={(event) => props.onQuestionChange(event.target.value)}
        placeholder="Ask your database anything..."
        className="min-h-40 text-[15px] leading-relaxed"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[140px_160px_minmax(0,1fr)_auto]">
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold uppercase tracking-wide text-zinc-500">Max Rows</label>
          <Input
            type="number"
            min={1}
            max={1000}
            value={props.maxRows}
            onChange={(event) => props.onMaxRowsChange(Number(event.target.value || 20))}
          />
        </div>

        <div className="space-y-1.5">
          <label className="block text-xs font-semibold uppercase tracking-wide text-zinc-500">Enable LLM</label>
          <button
            type="button"
            onClick={() => props.onLLMEnabledChange(!props.llmEnabled)}
            className={`inline-flex h-11 w-full items-center rounded-xl border px-3 text-sm font-semibold transition ${
              props.llmEnabled
                ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                : "border-zinc-200 bg-white text-zinc-500 hover:bg-zinc-50"
            }`}
          >
            {props.llmEnabled ? "Enabled" : "Disabled"}
          </button>
        </div>

        <div className="space-y-1.5">
          <label className="block text-xs font-semibold uppercase tracking-wide text-zinc-500">Model (Optional)</label>
          <Input
            value={props.model}
            onChange={(event) => props.onModelChange(event.target.value)}
            placeholder="gpt-4o-mini"
          />
        </div>

        <div className="flex items-end">
          <Button onClick={props.onRun} disabled={!props.canRun || props.running} className="h-11 w-full lg:w-[140px]">
            {props.running ? (
              <span className="inline-flex items-center gap-2">
                <Spinner />
                Running
              </span>
            ) : (
              <span className="inline-flex items-center gap-2">
                <Play className="h-4 w-4" />
                Run Query
              </span>
            )}
          </Button>
        </div>
      </div>

      {props.llmEnabled && (
        <div className="grid grid-cols-1 gap-4 rounded-2xl border border-zinc-200 bg-zinc-50/70 p-4 lg:grid-cols-2">
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold uppercase tracking-wide text-zinc-500">OpenAI API Key</label>
            <Input
              type="password"
              autoComplete="off"
              value={props.apiKey}
              onChange={(event) => props.onApiKeyChange(event.target.value)}
              placeholder="sk-..."
            />
            <p className="text-xs text-zinc-500">留空时将使用后端环境变量中的 OPENAI_API_KEY。</p>
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold uppercase tracking-wide text-zinc-500">Base URL (Optional)</label>
            <Input
              value={props.baseUrl}
              onChange={(event) => props.onBaseUrlChange(event.target.value)}
              placeholder="https://api.openai.com/v1"
            />
            <p className="text-xs text-zinc-500">用于兼容代理网关或第三方 OpenAI 兼容端点。</p>
          </div>
        </div>
      )}
    </Card>
  );
}
