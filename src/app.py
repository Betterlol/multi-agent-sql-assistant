"""Vercel FastAPI entrypoint.

Vercel zero-config detection supports `src/app.py` with a module-level `app`.
"""

from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parent
if str(SRC_ROOT) not in sys.path:
    # Ensure `multi_agent_sql_assistant` is importable when this file is executed by path.
    sys.path.insert(0, str(SRC_ROOT))

from multi_agent_sql_assistant.app import create_app

app = create_app()
