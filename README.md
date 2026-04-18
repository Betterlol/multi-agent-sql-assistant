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

启动后访问 `http://127.0.0.1:8000/` 可使用内置前端交互页面。

## Prepare demo database
```bash
python scripts/init_sample_db.py --db-path sample_data/sample.sqlite --orders 120 --seed 2026
```

然后在前端页面把数据库路径填为项目内绝对路径，例如：
`/mnt/e/Git/warehouse/Working/agent/github-local-repos/multi-agent-sql-assistant/sample_data/sample.sqlite`

## API usage
### Health
```bash
curl http://127.0.0.1:8000/health
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

Response fields include:
- `plan_intent`
- `selected_table`
- `generated_sql`
- `verified_sql`
- `warnings`
- `columns`, `rows`, `row_count`

## Frontend interaction
Web UI (`/`) supports:
- 输入 SQLite 数据库路径
- 输入自然语言问题
- 配置 `max_rows`
- 展示 planner intent、生成 SQL、校验 SQL、warnings
- 表格渲染查询结果

默认请求接口：`POST /v1/query`

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

## Current limitations
- SQLite only
- LLM generation still depends on prompt quality
- Schema-linking is heuristic-first (LLM optional)

## Next steps
- Add execution plan introspection and explain endpoint
- Add benchmark suite for accuracy/latency/cost trade-offs
