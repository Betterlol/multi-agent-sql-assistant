import type { MetricsResponse, QueryResponse, UploadResponse } from "./types";

class ApiError extends Error {
  status: number;

  constructor(message: string, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseError(response: Response): Promise<ApiError> {
  try {
    const payload = await response.json();
    const detail = typeof payload?.detail === "string" ? payload.detail : `Request failed (${response.status})`;
    return new ApiError(detail, response.status);
  } catch {
    return new ApiError(`Request failed (${response.status})`, response.status);
  }
}

export async function uploadDatabase(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/v1/database/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  return (await response.json()) as UploadResponse;
}

export interface RunQueryInput {
  database_id: string;
  question: string;
  max_rows: number;
  llm: {
    enabled: boolean;
    provider: string;
    api_key?: string | null;
    model?: string | null;
    base_url?: string | null;
  };
}

export async function runQuery(input: RunQueryInput): Promise<QueryResponse> {
  const response = await fetch("/v1/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  return (await response.json()) as QueryResponse;
}

export async function fetchMetrics(): Promise<MetricsResponse> {
  const response = await fetch("/v1/metrics", { method: "GET" });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MetricsResponse;
}

export { ApiError };
