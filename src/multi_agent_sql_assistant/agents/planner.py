from __future__ import annotations

import re

from ..types import QueryPlan


class PlannerAgent:
    def plan(self, question: str) -> QueryPlan:
        lowered = question.lower().strip()
        if not lowered:
            raise ValueError("Question is required.")

        intent = self._detect_intent(lowered)
        limit = self._extract_limit(lowered)
        table_hint = self._extract_table_hint(lowered)
        sort_note = self._extract_sort_preference(lowered)

        notes: list[str] = []
        if table_hint:
            notes.append(f"Detected table hint: {table_hint}")
        if sort_note:
            notes.append(sort_note)
        notes.append(f"Intent classified as: {intent}")

        return QueryPlan(intent=intent, table_hint=table_hint, limit=limit, notes=notes)

    def _detect_intent(self, question: str) -> str:
        if any(token in question for token in ["how many", "count", "total number", "多少", "数量"]):
            return "count"
        if any(token in question for token in ["top", "highest", "largest", "most"]):
            return "top"
        if any(token in question for token in ["find", "search", "look for", "搜索", "查找"]):
            return "list"
        return "list"

    def _extract_limit(self, question: str) -> int:
        patterns = [
            r"(?:top|first|last|limit|show)\s+(\d+)",
            r"前\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                parsed = int(match.group(1))
                return min(max(parsed, 1), 500)
        return 20

    def _extract_table_hint(self, question: str) -> str | None:
        patterns = [
            r"from\s+([a-zA-Z_][\w]*)",
            r"in\s+([a-zA-Z_][\w]*)",
            r"table\s+([a-zA-Z_][\w]*)",
        ]
        for pattern in patterns:
            matched = re.search(pattern, question)
            if matched:
                return matched.group(1)
        return None

    def _extract_sort_preference(self, question: str) -> str | None:
        if any(token in question for token in ["latest", "newest", "recent", "最新", "最近"]):
            return "Sort preference: updated_at desc"
        if any(token in question for token in ["highest", "largest", "biggest"]):
            return "Sort preference: numeric desc"
        return None
