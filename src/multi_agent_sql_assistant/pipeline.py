from __future__ import annotations

from dataclasses import dataclass

from .agents.generator import SQLGeneratorAgent
from .agents.planner import PlannerAgent
from .agents.spec_verifier import QuerySpecVerifier
from .agents.sql_builder import SQLBuilder
from .agents.verifier import VerifierAgent
from .database import DatabaseSchema
from .types import GeneratedQuery, QueryPlan, QuerySpec, VerifiedQuery, VerifiedQuerySpec


@dataclass(frozen=True)
class PipelineResult:
    plan: QueryPlan
    query_spec: QuerySpec
    verified_query_spec: VerifiedQuerySpec
    generated_query: GeneratedQuery
    verified_query: VerifiedQuery


class SQLAssistantPipeline:
    def __init__(
        self,
        planner: PlannerAgent | None = None,
        generator: SQLGeneratorAgent | None = None,
        spec_verifier: QuerySpecVerifier | None = None,
        sql_builder: SQLBuilder | None = None,
        verifier: VerifierAgent | None = None,
    ) -> None:
        self.planner = planner or PlannerAgent()
        self.generator = generator or SQLGeneratorAgent()
        self.spec_verifier = spec_verifier or QuerySpecVerifier()
        self.sql_builder = sql_builder or SQLBuilder()
        self.verifier = verifier or VerifierAgent()

    def run(self, question: str, schema: DatabaseSchema, max_rows: int = 100) -> PipelineResult:
        plan = self.planner.plan(question)
        query_spec = self.generator.generate_spec(question=question, plan=plan, schema=schema)
        verified_spec = self.spec_verifier.verify(spec=query_spec, schema=schema, max_limit=max_rows)
        generated = self.sql_builder.build(verified_spec)
        verified = self.verifier.verify(generated.sql, schema=schema, max_limit=max_rows)
        return PipelineResult(
            plan=plan,
            query_spec=query_spec,
            verified_query_spec=verified_spec,
            generated_query=generated,
            verified_query=verified,
        )
