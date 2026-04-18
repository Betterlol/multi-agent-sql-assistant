# Architecture Notes

## Pipeline contract
- Input: natural language question + database schema
- Output: verified SQL + execution result

## Agents
- Planner: intent classification and hint extraction
- Generator: optional LLM generation with deterministic heuristic fallback
- Verifier: guardrails (single statement, read-only, table existence, row limits)

## Safety rules
- Reject non-SELECT and multi-statement SQL
- Block mutating keywords (INSERT/UPDATE/DELETE/etc.)
- Reject unknown tables referenced in FROM/JOIN
- Enforce configurable LIMIT caps
