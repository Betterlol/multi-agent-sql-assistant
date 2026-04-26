"""Vercel FastAPI entrypoint.

Vercel zero-config detection supports `src/app.py` with a module-level `app`.
"""

from .multi_agent_sql_assistant.app import create_app

app = create_app()
