import { AlertTriangle } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ApiError, fetchMetrics, runQuery, uploadDatabase } from "./lib/api";
import type {
  HistoryItem,
  MetricsResponse,
  QueryResponse,
  TableSchema,
  UploadResponse,
} from "./lib/types";
import { loadHistory, saveHistory } from "./lib/utils";
import { BuiltSQLPanel } from "./components/debug/BuiltSQLPanel";
import { ParamsPanel } from "./components/debug/ParamsPanel";
import { QuerySpecPanel } from "./components/debug/QuerySpecPanel";
import { VerifiedSQLPanel } from "./components/debug/VerifiedSQLPanel";
import { WarningsPanel } from "./components/debug/WarningsPanel";
import { AppLayout } from "./components/layout/AppLayout";
import { Sidebar } from "./components/layout/Sidebar";
import { TopBar } from "./components/layout/TopBar";
import { QueryComposer } from "./components/query/QueryComposer";
import { QueryHistory } from "./components/query/QueryHistory";
import { ResultStats } from "./components/result/ResultStats";
import { ResultTable } from "./components/result/ResultTable";
import { UploadPanel } from "./components/upload/UploadPanel";
import { Card } from "./components/ui/Card";
import { Tabs, type TabItem } from "./components/ui/Tabs";

export default function App() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [backendOk, setBackendOk] = useState(true);

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadInfo, setUploadInfo] = useState<UploadResponse | null>(null);
  const [tableSchema, setTableSchema] = useState<TableSchema>({});

  const [question, setQuestion] = useState("");
  const [maxRows, setMaxRows] = useState(100);
  const [llmEnabled, setLlmEnabled] = useState(false);
  const [model, setModel] = useState("");

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [history, setHistory] = useState<HistoryItem[]>(() => loadHistory());

  useEffect(() => {
    saveHistory(history);
  }, [history]);

  const refreshMetrics = useCallback(async () => {
    try {
      const next = await fetchMetrics();
      setMetrics(next);
      setBackendOk(true);
    } catch {
      setBackendOk(false);
    }
  }, []);

  useEffect(() => {
    refreshMetrics();
    const timer = setInterval(refreshMetrics, 10000);
    return () => clearInterval(timer);
  }, [refreshMetrics]);

  const addHistory = useCallback((item: Omit<HistoryItem, "id">) => {
    const next: HistoryItem = {
      id: `${item.timestamp}-${Math.random().toString(36).slice(2, 8)}`,
      ...item,
    };
    setHistory((prev) => [next, ...prev].slice(0, 30));
  }, []);

  const handleUpload = useCallback(async () => {
    if (!file) {
      setError("请先选择 SQLite 文件");
      return;
    }

    setError(null);
    setUploading(true);
    try {
      const info = await uploadDatabase(file);
      setUploadInfo(info);
      setTableSchema(info.table_schema ?? Object.fromEntries((info.table_names || []).map((name) => [name, []])));
      setBackendOk(true);
      await refreshMetrics();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "上传失败";
      setError(message);
      setBackendOk(false);
    } finally {
      setUploading(false);
    }
  }, [file, refreshMetrics]);

  const handleRun = useCallback(async () => {
    if (!uploadInfo?.database_id) {
      setError("请先上传数据库");
      return;
    }
    if (!question.trim()) {
      setError("请输入问题");
      return;
    }

    setError(null);
    setRunning(true);
    const started = performance.now();
    try {
      const response = await runQuery({
        database_id: uploadInfo.database_id,
        question: question.trim(),
        max_rows: maxRows,
        llm: {
          enabled: llmEnabled,
          provider: "openai",
          model: model.trim() || null,
        },
      });
      setResult(response);
      setLatencyMs(Math.round(performance.now() - started));
      setBackendOk(true);
      addHistory({ question: question.trim(), timestamp: Date.now(), success: true });
      await refreshMetrics();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "查询失败";
      setError(message);
      setBackendOk(false);
      addHistory({ question: question.trim(), timestamp: Date.now(), success: false });
    } finally {
      setRunning(false);
    }
  }, [addHistory, llmEnabled, maxRows, model, question, refreshMetrics, uploadInfo?.database_id]);

  const handleHistorySelect = useCallback((item: HistoryItem) => {
    setQuestion(item.question);
  }, []);

  const debugTabs = useMemo<TabItem[]>(
    () => [
      {
        key: "spec",
        label: "QuerySpec",
        content: <QuerySpecPanel value={result?.query_spec ?? null} />,
      },
      {
        key: "built",
        label: "Built SQL",
        content: <BuiltSQLPanel sql={result?.built_sql ?? result?.generated_sql ?? null} />,
      },
      {
        key: "params",
        label: "SQL Params",
        content: <ParamsPanel params={result?.sql_params ?? []} />,
      },
      {
        key: "verified",
        label: "Verified SQL",
        content: <VerifiedSQLPanel sql={result?.verified_sql ?? null} />,
      },
      {
        key: "warnings",
        label: "Warnings",
        content: <WarningsPanel warnings={result?.warnings ?? []} specWarnings={result?.spec_warnings ?? []} />,
      },
    ],
    [result]
  );

  return (
    <AppLayout
      sidebar={<Sidebar tableSchema={tableSchema} tableCount={uploadInfo?.table_count ?? 0} />}
      topbar={<TopBar metrics={metrics} backendOk={backendOk} />}
    >
      <div className="space-y-4">
        {error && (
          <Card className="border-rose-900 bg-rose-950/40 text-rose-200">
            <div className="inline-flex items-center gap-2 text-sm">
              <AlertTriangle className="h-4 w-4" />
              {error}
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 gap-4 xl:grid-cols-[360px_minmax(0,1fr)]">
          <div className="space-y-4">
            <UploadPanel
              file={file}
              uploading={uploading}
              uploadInfo={uploadInfo}
              onFileChange={setFile}
              onUpload={handleUpload}
            />
            <QueryHistory items={history} onSelect={handleHistorySelect} />
          </div>

          <div className="space-y-4">
            <QueryComposer
              question={question}
              maxRows={maxRows}
              llmEnabled={llmEnabled}
              model={model}
              running={running}
              canRun={Boolean(uploadInfo?.database_id)}
              onQuestionChange={setQuestion}
              onMaxRowsChange={setMaxRows}
              onLLMEnabledChange={setLlmEnabled}
              onModelChange={setModel}
              onRun={handleRun}
            />

            <ResultStats
              rowCount={result?.row_count ?? 0}
              selectedTable={result?.selected_table ?? "-"}
              intent={result?.plan_intent ?? "-"}
              latencyMs={latencyMs}
            />

            <ResultTable columns={result?.columns ?? []} rows={result?.rows ?? []} />

            <Card>
              <div className="mb-3 text-sm font-semibold text-slate-200">Debug Panels</div>
              <Tabs items={debugTabs} defaultKey="spec" />
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
