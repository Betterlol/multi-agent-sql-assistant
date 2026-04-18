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


def test_verifier_blocks_multi_statement_sql() -> None:
    verifier = VerifierAgent()
    schema = DatabaseSchema(tables={"orders": ["id", "amount"]})

    with pytest.raises(SQLVerificationError):
        verifier.verify("SELECT * FROM orders; SELECT * FROM orders", schema=schema)


def test_verifier_blocks_unknown_table() -> None:
    verifier = VerifierAgent()
    schema = DatabaseSchema(tables={"orders": ["id", "amount"]})

    with pytest.raises(SQLVerificationError):
        verifier.verify("SELECT * FROM payments", schema=schema)


def test_verifier_reduces_limit_when_too_large() -> None:
    verifier = VerifierAgent()
    schema = DatabaseSchema(tables={"orders": ["id", "amount"]})

    verified = verifier.verify("SELECT * FROM orders LIMIT 5000", schema=schema, max_limit=100)

    assert "LIMIT 100" in verified.sql.upper()
    assert verified.warnings == ["LIMIT reduced from 5000 to 100."]
