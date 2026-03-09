from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, List, Optional


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
    """Deprecated: SQL validation functions no longer used in AR agent (uses JSON loader instead)."""
    raise NotImplementedError("SQL validation deprecated - AR agent uses JSON loader")


def validate_column(table: str, column: str) -> None:
    """Deprecated: SQL validation functions no longer used in AR agent (uses JSON loader instead)."""
    raise NotImplementedError("SQL validation deprecated - AR agent uses JSON loader")


def validate_select(table: str, select: Optional[List[str]]) -> List[str]:
    """Deprecated: SQL validation functions no longer used in AR agent (uses JSON loader instead)."""
    raise NotImplementedError("SQL validation deprecated - AR agent uses JSON loader")