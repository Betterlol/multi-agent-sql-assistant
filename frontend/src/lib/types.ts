export type Primitive = string | number | boolean | null;

export interface QueryFilter {
  field: string;
  op: string;
  value?: Primitive | Primitive[];
  value2?: Primitive;
}

export interface QuerySort {
  field: string;
  direction: "asc" | "desc" | string;
}

export interface QuerySearch {
  query: string;
  fields: string[];
}

export interface QuerySpec {
  target_table: string;
  select: string[];
  filters: QueryFilter[];
  search: QuerySearch | null;
  sort: QuerySort[];
  limit: number;
  offset: number;
  mode: "list" | "count" | string;
  reasoning: string;
}

export interface BuiltQuery {
  sql: string;
  params: Primitive[];
  selected_table: string;
  reasoning: string;
}

export type QueryWarning = string;

export type TableSchema = Record<string, string[]>;

export interface QueryResponse {
  request_id: string;
  plan_intent: string;
  selected_table: string;
  generated_sql: string;
  verified_sql: string;
  built_sql?: string | null;
  sql_params?: Primitive[] | null;
  warnings: QueryWarning[];
  query_spec?: QuerySpec | null;
  spec_warnings?: QueryWarning[];
  columns: string[];
  rows: Primitive[][];
  row_count: number;
}

export interface MetricsResponse {
  uploads_total: number;
  uploads_failed: number;
  uploads_active: number;
  queries_total: number;
  queries_success: number;
  queries_failed: number;
  llm_enabled_queries: number;
  llm_fallback_queries: number;
  latency_ms: {
    avg: number;
    p50: number;
    p95: number;
    samples: number;
  };
}

export interface UploadResponse {
  request_id: string;
  database_id: string;
  filename: string;
  table_names: string[];
  table_count: number;
  expires_at: number;
  table_schema?: TableSchema;
}

export interface HistoryItem {
  id: string;
  question: string;
  timestamp: number;
  success: boolean;
}
