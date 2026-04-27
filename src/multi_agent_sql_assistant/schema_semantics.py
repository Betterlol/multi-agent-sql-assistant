from __future__ import annotations

from dataclasses import dataclass, field

from .database import DatabaseSchema


@dataclass(frozen=True)
class FieldSemantic:
    name: str
    aliases: list[str]
    field_type: str
    searchable: bool = False
    sortable: bool = False
    filterable: bool = True


@dataclass(frozen=True)
class TableSemantic:
    name: str
    aliases: list[str]
    fields: dict[str, FieldSemantic] = field(default_factory=dict)


@dataclass(frozen=True)
class SchemaSemantics:
    tables: dict[str, TableSemantic] = field(default_factory=dict)


_SEARCHABLE_TOKENS = {"title", "name", "description", "note", "summary", "author"}
_SORTABLE_TOKENS = {"created_at", "updated_at", "rating", "amount", "score"}


def build_default_semantics(schema: DatabaseSchema) -> SchemaSemantics:
    tables: dict[str, TableSemantic] = {}

    for table_name, columns in schema.tables.items():
        field_semantics: dict[str, FieldSemantic] = {}
        for column in columns:
            normalized = column.lower()
            field_type = _infer_field_type(normalized)
            searchable = any(token in normalized for token in _SEARCHABLE_TOKENS)
            sortable = any(token in normalized for token in _SORTABLE_TOKENS)
            aliases = _build_aliases(column)

            field_semantics[column.lower()] = FieldSemantic(
                name=column,
                aliases=aliases,
                field_type=field_type,
                searchable=searchable,
                sortable=sortable,
                filterable=True,
            )

        table_aliases = _build_aliases(table_name)
        tables[table_name.lower()] = TableSemantic(
            name=table_name,
            aliases=table_aliases,
            fields=field_semantics,
        )

    return SchemaSemantics(tables=tables)


def _infer_field_type(field_name: str) -> str:
    if field_name == "id" or field_name.endswith("_id"):
        return "integer"
    if field_name.endswith("_at"):
        return "datetime"
    if any(token in field_name for token in ("rating", "score", "amount", "price", "total")):
        return "number"
    return "text"


def _build_aliases(name: str) -> list[str]:
    lowered = name.lower()
    aliases = {lowered, lowered.replace("_", " ")}
    if lowered.endswith("s") and len(lowered) > 1:
        aliases.add(lowered[:-1])
    return sorted(aliases)
