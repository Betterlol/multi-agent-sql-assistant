from __future__ import annotations

import pytest

from multi_agent_sql_assistant.agents.verifier import SQLVerificationError, VerifierAgent
from multi_agent_sql_assistant.database import DatabaseSchema


def test_verifier_blocks_dangerous_keywords() -> None:
    verifier = VerifierAgent()
    schema = DatabaseSchema(tables={"orders": ["id", "amount"]})

    with pytest.raises(SQLVerificationError):
        verifier.verify("DELETE FROM orders", schema=schema)


def test_verifier_adds_limit_if_missing() -> None:
    verifier = VerifierAgent()
    schema = DatabaseSchema(tables={"orders": ["id", "amount"]})

    verified = verifier.verify('SELECT * FROM "orders"', schema=schema, max_limit=50)

    assert verified.sql.endswith("LIMIT 50")
    assert verified.warnings
