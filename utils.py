from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, List, Optional

from constants import TABLES


def quote_ident(name: str) -> str:
    # very strict identifier validation to avoid injection via columns/tables
    if not name or not name.replace("_", "").isalnum():
        raise ValueError(f"Invalid identifier: {name}")
    return name


def format_value(v: Any) -> str:
    """
    Render a literal SQL value safely (basic, DB-agnostic).
    NOTE: Best practice is parameterized queries; but since you're returning a fully rendered SQL string,
    we do strict escaping here.
    """
    if v is None:
        return "NULL"

    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"

    if isinstance(v, (int, float, Decimal)):
        return str(v)

    if isinstance(v, (date, datetime)):
        return f"'{v.isoformat()}'"

    if isinstance(v, str):
        escaped = v.replace("'", "''")
        return f"'{escaped}'"

    raise ValueError(f"Unsupported value type: {type(v)}")


def validate_table(table: str) -> None:
    if table not in TABLES:
        raise ValueError(f"Table not allowed: {table}. Allowed: {sorted(TABLES.keys())}")


def validate_column(table: str, column: str) -> None:
    validate_table(table)
    if column not in TABLES[table]:
        raise ValueError(f"Column not allowed for {table}: {column}. Allowed: {sorted(TABLES[table])}")


def validate_select(table: str, select: Optional[List[str]]) -> List[str]:
    validate_table(table)
    if not select:
        # caller can decide defaults; we keep '*' disallowed by default
        raise ValueError("select must be provided (explicit columns only).")

    cols: List[str] = []
    for c in select:
        validate_column(table, c)
        cols.append(quote_ident(c))
    return cols