import { Play } from "lucide-react";

import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Input } from "../ui/Input";
import { Spinner } from "../ui/Spinner";
import { Textarea } from "../ui/Textarea";

interface QueryComposerProps {
  question: string;
  maxRows: number;
  llmEnabled: boolean;
  model: string;
  running: boolean;
  canRun: boolean;
  onQuestionChange: (value: string) => void;
  onMaxRowsChange: (value: number) => void;
  onLLMEnabledChange: (value: boolean) => void;
  onModelChange: (value: string) => void;
  onRun: () => void;
}

export function QueryComposer(props: QueryComposerProps) {
  return (
    <Card className="space-y-3">
      <div className="text-sm font-semibold text-slate-200">Query Composer</div>

      <Textarea
        value={props.question}
        onChange={(event) => props.onQuestionChange(event.target.value)}
        placeholder="例如：search dragon works updated recently"
      />

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div>
          <label className="mb-1 block text-xs text-slate-400">max_rows</label>
          <Input
            type="number"
            min={1}
            max={1000}
            value={props.maxRows}
            onChange={(event) => props.onMaxRowsChange(Number(event.target.value || 20))}
          />
        </div>
        <div>
          <label className="mb-1 block text-xs text-slate-400">Enable LLM</label>
          <div className="flex h-9 items-center rounded-md border border-slate-700 bg-slate-950 px-3">
            <input
              type="checkbox"
              checked={props.llmEnabled}
              onChange={(event) => props.onLLMEnabledChange(event.target.checked)}
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-xs text-slate-400">model (optional)</label>
          <Input
            value={props.model}
            onChange={(event) => props.onModelChange(event.target.value)}
            placeholder="gpt-4o-mini"
          />
        </div>
      </div>

      <Button onClick={props.onRun} disabled={!props.canRun || props.running}>
        {props.running ? (
          <span className="inline-flex items-center gap-2">
            <Spinner />
            Running...
          </span>
        ) : (
          <span className="inline-flex items-center gap-2">
            <Play className="h-4 w-4" />
            Run Query
          </span>
        )}
      </Button>
    </Card>
  );
}
