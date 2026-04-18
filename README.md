# Multi-Agent SQL Assistant

Natural language to SQL with a three-stage pipeline:
- Planner Agent
- SQL Generator Agent
- Verifier Agent (safety guardrails)

This MVP runs on SQLite and exposes a FastAPI endpoint for query generation and execution.

## Why this project
This repository demonstrates practical agent engineering for real-world data tasks:
- Structured multi-agent orchestration (plan -> generate -> verify)
- Query safety checks (read-only, single statement, table validation, limit enforcement)
- End-to-end API integration with executable SQL results

## Architecture
1. Planner analyzes question intent (`count`, `top`, `list`) and extracts hints.
2. Generator selects a table via schema-linking heuristics and drafts SQL.
3. Verifier uses SQL AST parsing (`sqlglot`) to block dangerous SQL and enforce a safe row limit.
4. SQLite client executes verified SQL and returns rows.

## Project structure
- `src/multi_agent_sql_assistant/agents/`: planner, generator, verifier
- `src/multi_agent_sql_assistant/database.py`: schema inspection + SQL execution
- `src/multi_agent_sql_assistant/pipeline.py`: orchestrates agents
- `src/multi_agent_sql_assistant/app.py`: FastAPI endpoints
- `src/multi_agent_sql_assistant/upload_registry.py`: persistent upload registry with TTL cleanup
- `src/multi_agent_sql_assistant/observability.py`: structured logs and in-memory metrics
- `tests/`: unit and API tests
- `docs/`: roadmap and architecture notes

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]

# run tests
pytest -q

# run API
uvicorn src.main:app --reload
```

启动后访问 `http://127.0.0.1:8000/` 可使用内置前端交互页面（支持直接选择 SQLite 文件上传）。

## Prepare demo database
```bash
python scripts/init_sample_db.py --db-path sample_data/sample.sqlite --orders 120 --seed 2026
```

前端页面现在可直接选择该文件进行上传，不需要手填路径。

## API usage
### Health
```bash
curl http://127.0.0.1:8000/health
```

### Metrics
```bash
curl http://127.0.0.1:8000/metrics
```

### Query endpoint
```bash
curl -X POST http://127.0.0.1:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{
    "database_path": "./sample.sqlite",
    "question": "How many orders are there?",
    "max_rows": 100
  }'
```

### Upload database (for frontend / file mode)
```bash
curl -X POST http://127.0.0.1:8000/v1/upload-db \
  -F "file=@sample_data/sample.sqlite"
```

上传成功后可使用 `database_id` 查询：
```bash
curl -X POST http://127.0.0.1:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{
    "database_id": "YOUR_DATABASE_ID",
    "question": "How many orders are there?",
    "max_rows": 100
  }'
```

也支持在查询请求里传入临时 LLM 配置（覆盖当前请求）：
```bash
curl -X POST http://127.0.0.1:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{
    "database_id": "YOUR_DATABASE_ID",
    "question": "List top 5 orders by amount",
    "max_rows": 100,
    "llm": {
      "enabled": true,
      "provider": "openai",
      "api_key": "YOUR_OPENAI_KEY",
      "model": "gpt-4o-mini",
      "base_url": "https://api.openai.com/v1"
    }
  }'
```

Response fields include:
- `plan_intent`
- `selected_table`
- `generated_sql`
- `verified_sql`
- `warnings`
- `columns`, `rows`, `row_count`

## Frontend interaction
Web UI (`/`) supports:
- 选择 SQLite 文件并自动上传
- 输入自然语言问题
- 配置 `max_rows`
- 选择并填写 LLM 配置（provider/api key/model/base url）
- 展示 planner intent、生成 SQL、校验 SQL、warnings
- 表格渲染查询结果

默认请求接口：`POST /v1/query`

## Upload lifecycle
- Uploaded files are persisted under `runtime_uploads/files/`.
- Upload metadata is persisted in `runtime_uploads/registry.sqlite`.
- Expired uploads are cleaned automatically based on TTL (`SQL_ASSISTANT_UPLOAD_TTL_SECONDS`).
- Default TTL: 86400 seconds (24 hours).

## Optional LLM mode (OpenAI)
By default, SQL generation is heuristic. To enable LLM-backed generation with automatic fallback:

```bash
export SQL_ASSISTANT_LLM_PROVIDER=openai
export OPENAI_API_KEY=your_api_key
# optional
export SQL_ASSISTANT_OPENAI_MODEL=gpt-4o-mini
export SQL_ASSISTANT_OPENAI_BASE_URL=https://api.openai.com/v1
```

If LLM generation fails for any reason, the service falls back to deterministic heuristic generation.

## Docker deployment
```bash
cp .env.example .env
docker compose up --build
```

Then open:
- `http://127.0.0.1:8000/` (web UI)
- `http://127.0.0.1:8000/metrics` (runtime metrics)

## Current limitations
- SQLite only
- LLM generation still depends on prompt quality
- Schema-linking is heuristic-first (LLM optional)

## Next steps
- Add execution plan introspection and explain endpoint
- Add benchmark suite for accuracy/latency/cost trade-offs
