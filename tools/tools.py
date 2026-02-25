from typing import Any, Dict, Optional, Tuple, List, Literal
from langchain.tools import tool
from utils import format_value, validate_column, validate_select
from constants import OP, TABLE_NAME

@tool("update_credit_limit")
def update_credit_limit(
    employee_id: str,
    old_limit: int,
    new_limit: int,
    reason: str,
) -> Dict[str, Any]:
    """
    Build and return a COMPLETE SQL query to update an employee's credit limit. If you rename an employee_id, use the new employee_id for all subsequent operations.”

    Table: employees
    Columns: employee_id, credit_limit, credit_limit_reason

    NOTE:
    - This does NOT execute SQL
    - This returns a fully rendered SQL string
    """

    if not employee_id:
        return {"ok": False, "error": "employee_id is required."}

    if not isinstance(old_limit, int) or not isinstance(new_limit, int):
        return {"ok": False, "error": "old_limit and new_limit must be integers."}

    if new_limit <= 0:
        return {"ok": False, "error": "new_limit must be positive."}

    if not reason or not reason.strip():
        return {"ok": False, "error": "reason is required."}


    # Optimistic concurrency check included
    sql = (
        "UPDATE employees\n"
        f"SET credit_limit = {new_limit},\n"
        f"    credit_limit_reason = {reason}\n"
        f"WHERE employee_id = {employee_id}\n"
        f"  AND credit_limit = {old_limit};"
    )

    return {
        "ok": True,
        "sql": sql,
        "message": "Record updated succesfully."
    }

@tool("update_employee_id")
def update_employee_id(
    old_employee_id: str,
    new_employee_id: str,
) -> Dict[str, Any]:
    """
    Build SQL to update an employee's ID.
    """

    if not old_employee_id or not new_employee_id:
        return {"ok": False, "error": "Both old_employee_id and new_employee_id are required."}

    if old_employee_id == new_employee_id:
        return {"ok": False, "error": "old_employee_id and new_employee_id cannot be the same."}

    sql = (
    f"UPDATE employees\n"
    f"SET employee_id = '{new_employee_id}'\n"
    f"WHERE employee_id = '{old_employee_id}';"
)

    params: Tuple[Any, ...] = (new_employee_id, old_employee_id)

    return {
        "ok": True,
        "sql": sql,
        "message": "Record updated succesfully."
        # "params": params,
        # "notes": "Execute using parameterized query with your DB driver."
    }


@tool("search_database")
def search_database(
    # For now we keep it locked to employees. If later you want multiple tables,
    # we can add a `resource` enum and a per-resource allowlist.
    select: Optional[List[str]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    limit: int = 50,
    order_by: Optional[str] = None,
    order_dir: Literal["ASC", "DESC"] = "ASC",
) -> Dict[str, Any]:
    """
    Build a COMPLETE SQL query for fetching from the table.

    Inputs:
      select: list of columns to return (must be in ALLOWED_COLUMNS)
      filters: list of filter objects:
         {"column": "credit_limit", "op": ">", "value": 12000}
         {"column": "status", "op": "=", "value": "active"}
         {"column": "employee_id", "op": "IN", "value": ["emp_001","emp_002"]}

      limit: max rows (1..500)
      order_by: column name to order by (allowed only)
      order_dir: ASC/DESC

    Output:
      {"ok": True, "sql": "<final SQL string>"}

    NOTE:
    - This tool does NOT execute SQL (only builds it).
    - Table/columns are schema-locked to prevent hallucinations.
    """

    # validate limit
    if not isinstance(limit, int) or limit <= 0:
        return {"ok": False, "error": "limit must be a positive integer"}
    if limit > 500:
        return {"ok": False, "error": "limit too large (max 500)"}

    # validate select
    try:
        select_cols = validate_select(select or [])
    except Exception as e:
        return {"ok": False, "error": str(e)}

    where_clauses: List[str] = []

    # build filters
    if filters:
        for f in filters:
            col = f.get("column")
            op: OP = f.get("op")
            val = f.get("value")

            if not col or not op:
                return {"ok": False, "error": "Each filter needs 'column' and 'op'."}

            try:
                validate_column(col)
            except Exception as e:
                return {"ok": False, "error": str(e)}

            if op not in {"=", "!=", ">", ">=", "<", "<=", "IN", "LIKE"}:
                return {"ok": False, "error": f"Operator not allowed: {op}"}

            if op == "IN":
                if not isinstance(val, list) or len(val) == 0:
                    return {"ok": False, "error": "IN operator requires a non-empty list value"}
                in_list = ", ".join(format_value(x) for x in val)
                where_clauses.append(f"{col} IN ({in_list})")
            elif op == "LIKE":
                if not isinstance(val, str):
                    return {"ok": False, "error": "LIKE requires a string value"}
                where_clauses.append(f"{col} LIKE {format_value(val)}")
            else:
                where_clauses.append(f"{col} {op} {format_value(val)}")

    # validate order_by
    order_sql = ""
    if order_by:
        try:
            validate_column(order_by)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if order_dir not in {"ASC", "DESC"}:
            return {"ok": False, "error": "order_dir must be ASC or DESC"}
        order_sql = f"\nORDER BY {order_by} {order_dir}"

    sql = f"SELECT {', '.join(select_cols)}\nFROM {TABLE_NAME}"
    if where_clauses:
        sql += "\nWHERE " + " AND ".join(where_clauses)
    sql += order_sql
    sql += f"\nLIMIT {limit};"

    return {"ok": True, "sql": sql, "message": "Record ftched succesfully."}