import { AlertTriangle, FlaskConical } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

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
import { Card } from "./components/ui/Card";
import { Tabs, type TabItem } from "./components/ui/Tabs";
import { ApiError, fetchMetrics, runQuery, uploadDatabase } from "./lib/api";
import type {
  HistoryItem,
  MetricsResponse,
  QueryResponse,
  TableSchema,
  UploadResponse,
} from "./lib/types";
import { loadHistory, saveHistory } from "./lib/utils";

type ThemeMode = "light" | "dark";

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
  const [apiKey, setApiKey] = useState(() => {
    try {
      return localStorage.getItem("sql-assistant-openai-api-key") ?? "";
    } catch {
      return "";
    }
  });
  const [model, setModel] = useState("");
  const [baseUrl, setBaseUrl] = useState(() => {
    try {
      return localStorage.getItem("sql-assistant-openai-base-url") ?? "";
    } catch {
      return "";
    }
  });
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    try {
      const saved = localStorage.getItem("sql-assistant-theme-mode");
      if (saved === "dark" || saved === "light") {
        return saved;
      }
    } catch {
      // no-op
    }
    if (typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  });

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [history, setHistory] = useState<HistoryItem[]>(() => loadHistory());

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", themeMode === "dark");
    try {
      localStorage.setItem("sql-assistant-theme-mode", themeMode);
    } catch {
      // no-op
    }
  }, [themeMode]);

  useEffect(() => {
    saveHistory(history);
  }, [history]);

  useEffect(() => {
    try {
      localStorage.setItem("sql-assistant-openai-api-key", apiKey);
    } catch {
      // no-op
    }
  }, [apiKey]);

  useEffect(() => {
    try {
      localStorage.setItem("sql-assistant-openai-base-url", baseUrl);
    } catch {
      // no-op
    }
  }, [baseUrl]);

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
      setFile(null);
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
          api_key: apiKey.trim() || null,
          model: model.trim() || null,
          base_url: baseUrl.trim() || null,
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
  }, [addHistory, apiKey, baseUrl, llmEnabled, maxRows, model, question, refreshMetrics, uploadInfo?.database_id]);

  const handleHistorySelect = useCallback((item: HistoryItem) => {
    setQuestion(item.question);
  }, []);

  const handleToggleTheme = useCallback(() => {
    setThemeMode((current) => (current === "dark" ? "light" : "dark"));
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
        label: "SQL",
        content: <BuiltSQLPanel sql={result?.built_sql ?? result?.generated_sql ?? null} />,
      },
      {
        key: "params",
        label: "Params",
        content: <ParamsPanel params={result?.sql_params ?? []} />,
      },
      {
        key: "verified",
        label: "Verified",
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
      header={
        <TopBar
          metrics={metrics}
          backendOk={backendOk}
          file={file}
          uploading={uploading}
          uploadInfo={uploadInfo}
          themeMode={themeMode}
          onToggleTheme={handleToggleTheme}
          onFileChange={setFile}
          onUpload={handleUpload}
        />
      }
      sidebar={
        <>
          <Sidebar tableSchema={tableSchema} tableCount={uploadInfo?.table_count ?? 0} uploadInfo={uploadInfo} />
          <QueryHistory items={history} onSelect={handleHistorySelect} />
        </>
      }
      inspector={
        <Card className="flex h-full min-h-[460px] flex-col p-5 xl:min-h-0">
          <div className="mb-4 inline-flex items-center gap-2 text-sm font-semibold text-zinc-900 dark:text-zinc-100">
            <FlaskConical className="h-4 w-4 text-zinc-500 dark:text-zinc-400" />
            SQL Inspector
          </div>
          <div className="min-h-0 flex-1">
            <Tabs items={debugTabs} defaultKey="spec" />
          </div>
        </Card>
      }
    >
      <div className="space-y-6">
        {error && (
          <Card className="border-rose-200 bg-rose-50 p-4 text-rose-700 dark:border-rose-500/40 dark:bg-rose-500/15 dark:text-rose-200">
            <div className="inline-flex items-center gap-2 text-sm font-medium">
              <AlertTriangle className="h-4 w-4" />
              {error}
            </div>
          </Card>
        )}

        <QueryComposer
          question={question}
          maxRows={maxRows}
          llmEnabled={llmEnabled}
          apiKey={apiKey}
          model={model}
          baseUrl={baseUrl}
          running={running}
          canRun={Boolean(uploadInfo?.database_id)}
          onQuestionChange={setQuestion}
          onMaxRowsChange={setMaxRows}
          onLLMEnabledChange={setLlmEnabled}
          onApiKeyChange={setApiKey}
          onModelChange={setModel}
          onBaseUrlChange={setBaseUrl}
          onRun={handleRun}
        />

        <ResultStats
          rowCount={result?.row_count ?? 0}
          selectedTable={result?.selected_table ?? "-"}
          intent={result?.plan_intent ?? "-"}
          latencyMs={latencyMs}
        />

        <ResultTable columns={result?.columns ?? []} rows={result?.rows ?? []} />
      </div>
    </AppLayout>
  );
}
