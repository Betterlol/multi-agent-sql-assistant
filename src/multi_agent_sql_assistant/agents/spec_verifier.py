from __future__ import annotations

from ..database import DatabaseSchema
from ..schema_semantics import SchemaSemantics, build_default_semantics
from ..types import QueryFilter, QuerySearch, QuerySort, QuerySpec, VerifiedQuerySpec


class QuerySpecVerificationError(ValueError):
    pass


class QuerySpecVerifier:
    ALLOWED_OPS = {
        "=",
        "!=",
        ">",
        ">=",
        "<",
        "<=",
        "contains",
        "not_contains",
        "in",
        "between",
        "is_null",
        "is_not_null",
    }

    ALLOWED_MODES = {"list", "count"}
    ALLOWED_DIRECTIONS = {"asc", "desc"}

    def verify(
        self,
        spec: QuerySpec,
        schema: DatabaseSchema,
        max_limit: int = 100,
        semantics: SchemaSemantics | None = None,
    ) -> VerifiedQuerySpec:
        if not schema.tables:
            raise QuerySpecVerificationError("Database has no queryable tables.")

        semantic_model = semantics or build_default_semantics(schema)
        warnings: list[str] = []
        table_name = self._resolve_table(spec.target_table, schema)
        table_columns = schema.tables[table_name]
        table_semantic = semantic_model.tables.get(table_name.lower())

        normalized_select = self._normalize_select(spec.select, table_columns, warnings)
        normalized_filters = self._normalize_filters(spec.filters, table_columns)
        normalized_search = self._normalize_search(spec.search, table_columns, table_semantic, warnings)
        normalized_sort = self._normalize_sort(spec.sort, table_columns, table_semantic, warnings)
        normalized_limit = self._normalize_limit(spec.limit, max_limit=max_limit, warnings=warnings)
        normalized_offset = self._normalize_offset(spec.offset)
        normalized_mode = self._normalize_mode(spec.mode)

        normalized_spec = QuerySpec(
            target_table=table_name,
            select=normalized_select,
            filters=normalized_filters,
            search=normalized_search,
            sort=normalized_sort,
            limit=normalized_limit,
            offset=normalized_offset,
            mode=normalized_mode,
            reasoning=spec.reasoning,
        )
        return VerifiedQuerySpec(spec=normalized_spec, warnings=warnings)

    def _resolve_table(self, table_name: str, schema: DatabaseSchema) -> str:
        candidate = table_name.strip()
        if not candidate:
            raise QuerySpecVerificationError("target_table is required.")

        lookup = {name.lower(): name for name in schema.tables}
        matched = lookup.get(candidate.lower())
        if matched is None:
            raise QuerySpecVerificationError(f"Unknown target_table: {table_name}")
        return matched

    def _resolve_field(self, field_name: str, columns: list[str]) -> str:
        candidate = field_name.strip()
        if not candidate:
            raise QuerySpecVerificationError("Field name is required.")

        lookup = {name.lower(): name for name in columns}
        matched = lookup.get(candidate.lower())
        if matched is None:
            raise QuerySpecVerificationError(f"Unknown field: {field_name}")
        return matched

    def _normalize_select(self, select: list[str], columns: list[str], warnings: list[str]) -> list[str]:
        if not select:
            warnings.append("select was empty, defaulted to ['*']")
            return ["*"]

        if "*" in select:
            if len(select) > 1:
                warnings.append("select contained '*' with named fields, reduced to ['*']")
            return ["*"]

        normalized: list[str] = []
        for field in select:
            normalized.append(self._resolve_field(field, columns))
        return normalized

    def _normalize_filters(self, filters: list[QueryFilter], columns: list[str]) -> list[QueryFilter]:
        normalized: list[QueryFilter] = []
        for item in filters:
            op = item.op.strip().lower()
            if op not in self.ALLOWED_OPS:
                raise QuerySpecVerificationError(f"Unsupported filter op: {item.op}")
            field = self._resolve_field(item.field, columns)
            normalized.append(QueryFilter(field=field, op=op, value=item.value, value2=item.value2))
        return normalized

    def _normalize_search(
        self,
        search: QuerySearch | None,
        columns: list[str],
        table_semantic,
        warnings: list[str],
    ) -> QuerySearch | None:
        if search is None:
            return None

        query = search.query.strip()
        if not query:
            return None

        fields = list(search.fields)
        if not fields:
            semantic_fields: list[str] = []
            if table_semantic is not None:
                for semantic in table_semantic.fields.values():
                    if semantic.searchable:
                        semantic_fields.append(semantic.name)

            if semantic_fields:
                fields = semantic_fields
                warnings.append("search.fields was empty, defaulted to searchable fields")
            else:
                fields = list(columns)
                warnings.append("search.fields was empty and no searchable fields were found, defaulted to all fields")

        normalized_fields = [self._resolve_field(field, columns) for field in fields]
        return QuerySearch(query=query, fields=normalized_fields)

    def _normalize_sort(
        self,
        sort: list[QuerySort],
        columns: list[str],
        table_semantic,
        warnings: list[str],
    ) -> list[QuerySort]:
        normalized: list[QuerySort] = []
        for item in sort:
            direction = item.direction.strip().lower() if item.direction else "asc"
            if direction not in self.ALLOWED_DIRECTIONS:
                raise QuerySpecVerificationError(f"Unsupported sort direction: {item.direction}")

            field = self._resolve_field(item.field, columns)
            if table_semantic is not None:
                field_semantic = table_semantic.fields.get(field.lower())
                if field_semantic is not None and not field_semantic.sortable:
                    warnings.append(f"sorting by non-sortable semantic field: {field}")

            normalized.append(QuerySort(field=field, direction=direction))
        return normalized

    def _normalize_limit(self, limit: int, max_limit: int, warnings: list[str]) -> int:
        bounded_max = max(max_limit, 1)
        parsed_limit = self._coerce_int(limit, default=20)

        if parsed_limit < 1:
            warnings.append("limit was below 1, raised to 1")
            parsed_limit = 1
        if parsed_limit > bounded_max:
            warnings.append(f"limit reduced from {parsed_limit} to {bounded_max}")
            parsed_limit = bounded_max
        return parsed_limit

    def _normalize_offset(self, offset: int) -> int:
        parsed = self._coerce_int(offset, default=0)
        if parsed < 0:
            raise QuerySpecVerificationError("offset cannot be negative")
        return parsed

    def _normalize_mode(self, mode: str) -> str:
        normalized = mode.strip().lower() if mode else "list"
        if normalized not in self.ALLOWED_MODES:
            raise QuerySpecVerificationError(f"Unsupported mode: {mode}")
        return normalized

    def _coerce_int(self, value: object, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
