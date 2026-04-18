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
3. Verifier blocks dangerous SQL and enforces a safe row limit.
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

## Current limitations
- SQLite only
- Heuristic SQL generation (no LLM provider integration yet)
- Basic schema-linking strategy

## Next steps
- Add LLM-backed generator with fallback to heuristic mode
- Add SQL AST-level validation
- Add benchmark suite for accuracy/latency/cost trade-offs
