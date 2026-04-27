const form = document.getElementById("query-form");
const submitBtn = document.getElementById("submit-btn");

const errorBox = document.getElementById("error-box");
const resultPanel = document.getElementById("result-panel");

const planIntent = document.getElementById("plan-intent");
const selectedTable = document.getElementById("selected-table");
const rowCount = document.getElementById("row-count");
const latencyPill = document.getElementById("latency-pill");
const generatedSQL = document.getElementById("generated-sql");
const builtSQL = document.getElementById("built-sql");
const verifiedSQL = document.getElementById("verified-sql");
const sqlParams = document.getElementById("sql-params");
const querySpec = document.getElementById("query-spec");
const warningsList = document.getElementById("warnings");
const specWarningsList = document.getElementById("spec-warnings");
const resultTable = document.getElementById("result-table");

const dbFileInput = document.getElementById("database-file");
const dbStatus = document.getElementById("database-status");
const questionInput = document.getElementById("question");
const maxRowsInput = document.getElementById("max-rows");
const llmEnabledInput = document.getElementById("llm-enabled");
const llmFields = document.getElementById("llm-fields");
const llmProviderInput = document.getElementById("llm-provider");
const llmApiKeyInput = document.getElementById("llm-api-key");
const llmModelInput = document.getElementById("llm-model");
const llmBaseUrlInput = document.getElementById("llm-base-url");

let uploadedDatabaseId = null;
let uploadedFileFingerprint = null;

questionInput.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    form.requestSubmit();
  }
});

dbFileInput.addEventListener("change", () => {
  uploadedDatabaseId = null;
  uploadedFileFingerprint = null;
  const file = dbFileInput.files?.[0];
  if (!file) {
    dbStatus.textContent = "尚未选择文件";
    return;
  }
  dbStatus.textContent = `已选择：${file.name}（待上传）`;
});

llmEnabledInput.addEventListener("change", () => {
  llmFields.classList.toggle("hidden", !llmEnabledInput.checked);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();

  const question = questionInput.value.trim();
  const maxRows = Number(maxRowsInput.value);
  if (!question || !Number.isFinite(maxRows)) {
    showError("请填写完整参数（数据库文件、问题、最大返回行数）。");
    return;
  }

  const payload = {
    question,
    max_rows: maxRows,
    llm: buildLLMConfig(),
  };

  submitBtn.disabled = true;
  submitBtn.textContent = "执行中...";
  const start = performance.now();

  try {
    payload.database_id = await ensureDatabaseUploaded();

    const response = await fetch("/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const json = await response.json();
    if (!response.ok) {
      const detail = typeof json.detail === "string" ? json.detail : "查询执行失败";
      throw new Error(detail);
    }

    const elapsed = Math.round(performance.now() - start);
    renderResult(json, elapsed);
  } catch (error) {
    const message = error instanceof Error ? error.message : "未知错误";
    showError(`执行失败：${message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "运行查询";
  }
});

async function ensureDatabaseUploaded() {
  const file = dbFileInput.files?.[0];
  if (!file) {
    throw new Error("请先选择 SQLite 文件（.sqlite/.sqlite3/.db）");
  }

  const fingerprint = `${file.name}:${file.size}:${file.lastModified}`;
  if (uploadedDatabaseId && uploadedFileFingerprint === fingerprint) {
    return uploadedDatabaseId;
  }

  dbStatus.textContent = `上传中：${file.name}...`;
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/v1/upload-db", {
    method: "POST",
    body: formData,
  });
  const json = await response.json();
  if (!response.ok) {
    const detail = typeof json.detail === "string" ? json.detail : "数据库上传失败";
    throw new Error(detail);
  }

  uploadedDatabaseId = json.database_id;
  uploadedFileFingerprint = fingerprint;
  const tableNames = Array.isArray(json.table_names) ? json.table_names.join(", ") : "";
  dbStatus.textContent = `已上传：${json.filename}（${json.table_count} 张表：${tableNames}）`;
  return uploadedDatabaseId;
}

function buildLLMConfig() {
  if (!llmEnabledInput.checked) {
    return {
      enabled: false,
      provider: llmProviderInput.value || "openai",
    };
  }

  const provider = (llmProviderInput.value || "openai").trim().toLowerCase();
  const apiKey = llmApiKeyInput.value.trim();
  const model = llmModelInput.value.trim();
  const baseUrl = llmBaseUrlInput.value.trim();

  return {
    enabled: true,
    provider,
    api_key: apiKey || null,
    model: model || null,
    base_url: baseUrl || null,
  };
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function renderResult(data, elapsedMs) {
  resultPanel.classList.remove("hidden");
  planIntent.textContent = data.plan_intent;
  selectedTable.textContent = data.selected_table;
  rowCount.textContent = String(data.row_count);
  latencyPill.textContent = `${elapsedMs} ms`;

  generatedSQL.textContent = data.generated_sql || "-";
  builtSQL.textContent = data.built_sql || data.generated_sql || "-";
  verifiedSQL.textContent = data.verified_sql || "-";
  sqlParams.textContent = JSON.stringify(data.sql_params || [], null, 2);

  renderWarnings(warningsList, data.warnings || []);
  renderWarnings(specWarningsList, data.spec_warnings || []);
  renderQuerySpec(data.query_spec || null);
  renderTable(data.columns || [], data.rows || []);
}

function renderWarnings(container, warnings) {
  container.innerHTML = "";
  if (!warnings.length) {
    const li = document.createElement("li");
    li.textContent = "无";
    container.appendChild(li);
    return;
  }

  for (const warning of warnings) {
    const li = document.createElement("li");
    li.textContent = warning;
    container.appendChild(li);
  }
}

function renderQuerySpec(spec) {
  if (!spec) {
    querySpec.textContent = "-";
    return;
  }

  querySpec.textContent = JSON.stringify(spec, null, 2);
}

function renderTable(columns, rows) {
  resultTable.innerHTML = "";

  if (!columns.length) {
    const caption = document.createElement("caption");
    caption.textContent = "没有可展示的结果列";
    resultTable.appendChild(caption);
    return;
  }

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((column) => {
    const th = document.createElement("th");
    th.textContent = String(column);
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);

  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    row.forEach((cell) => {
      const td = document.createElement("td");
      td.textContent = cell === null ? "NULL" : String(cell);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  resultTable.appendChild(thead);
  resultTable.appendChild(tbody);
}
