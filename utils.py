from typing import Any, List
from constants import ALLOWED_COLUMNS

def escape_sql_str(value: str) -> str:
    """Minimal SQL escaping for string literals."""
    return "'" + value.replace("'", "''") + "'"


def format_value(v: Any) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return escape_sql_str(v)
    # fallback (you can tighten this)
    return escape_sql_str(str(v))


def validate_column(col: str) -> None:
    if col not in ALLOWED_COLUMNS:
        raise ValueError(f"Column not allowed: {col}")


def validate_select(select: List[str]) -> List[str]:
    if not select:
        return ["employee_id", "credit_limit"]  # default output
    for c in select:
        validate_column(c)
    return select