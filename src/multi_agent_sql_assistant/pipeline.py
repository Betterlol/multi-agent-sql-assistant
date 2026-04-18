from __future__ import annotations

from dataclasses import dataclass

from .agents.generator import SQLGeneratorAgent
from .agents.planner import PlannerAgent
from .agents.verifier import VerifierAgent
from .database import DatabaseSchema
from .types import GeneratedQuery, QueryPlan, VerifiedQuery


@dataclass(frozen=True)
class PipelineResult:
    plan: QueryPlan
    generated_query: GeneratedQuery
    verified_query: VerifiedQuery


class SQLAssistantPipeline:
    def __init__(
        self,
        planner: PlannerAgent | None = None,
        generator: SQLGeneratorAgent | None = None,
        verifier: VerifierAgent | None = None,
    ) -> None:
        self.planner = planner or PlannerAgent()
        self.generator = generator or SQLGeneratorAgent()
        self.verifier = verifier or VerifierAgent()

    def run(self, question: str, schema: DatabaseSchema, max_rows: int = 100) -> PipelineResult:
        plan = self.planner.plan(question)
        generated = self.generator.generate(question=question, plan=plan, schema=schema)
        verified = self.verifier.verify(generated.sql, schema=schema, max_limit=max_rows)
        return PipelineResult(plan=plan, generated_query=generated, verified_query=verified)
