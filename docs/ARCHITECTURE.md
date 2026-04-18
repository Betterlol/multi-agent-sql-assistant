# Architecture Notes

## Pipeline contract
- Input: natural language question + database schema
- Output: verified SQL + execution result

## Agents
- Planner: intent classification and hint extraction
- Generator: optional LLM generation with deterministic heuristic fallback
- Verifier: guardrails (single statement, read-only, table existence, row limits)

## Safety rules
- Parse SQL into AST via `sqlglot`
- Reject non-query / mutating statements and multi-statement input
- Reject unknown tables referenced in FROM/JOIN
- Enforce configurable LIMIT caps

## Upload storage
- Uploaded SQLite files are stored in `runtime_uploads/files`.
- Registry metadata is persisted in `runtime_uploads/registry.sqlite`.
- Expired files are removed via TTL cleanup.

## Observability
- Structured JSON logs for upload/query lifecycle.
- `/metrics` endpoint exposes counters and latency distribution (avg/p50/p95).
