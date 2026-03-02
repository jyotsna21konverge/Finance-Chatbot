from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from decimal import Decimal
from datetime import date
from data_loaders.db_executor import run_sql


from langchain.tools import tool

from constants import OP, ALLOWED_TABLES, DEFAULT_SELECT
from utils import format_value, validate_column, validate_select, validate_table, quote_ident


# -----------------------------
# Generic safe search across tables
# -----------------------------
@tool("search_table")
def search_table(
    table: Literal["customers", "cards", "expenses"],
    select: Optional[List[str]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    limit: int = 50,
    order_by: Optional[str] = None,
    order_dir: Literal["ASC", "DESC"] = "ASC",
) -> Dict[str, Any]:
    """
    Build a COMPLETE SQL query for fetching from customers/cards/expenses.

    filters examples:
      {"column": "customer_id", "op": "=", "value": 1}
      {"column": "category", "op": "LIKE", "value": "%Travel%"}
      {"column": "card_id", "op": "IN", "value": [1,2,3]}
    """

    try:
        validate_table(table)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    # validate limit
    if not isinstance(limit, int) or limit <= 0:
        return {"ok": False, "error": "limit must be a positive integer"}
    if limit > 500:
        return {"ok": False, "error": "limit too large (max 500)"}

    # select default if not provided
    if not select:
        select = DEFAULT_SELECT[table]

    try:
        select_cols = validate_select(table, select)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    where_clauses: List[str] = []

    if filters:
        for f in filters:
            col = f.get("column")
            op: OP = f.get("op")
            val = f.get("value")

            if not col or not op:
                return {"ok": False, "error": "Each filter needs 'column' and 'op'."}

            try:
                validate_column(table, col)
            except Exception as e:
                return {"ok": False, "error": str(e)}

            if op not in {"=", "!=", ">", ">=", "<", "<=", "IN", "LIKE"}:
                return {"ok": False, "error": f"Operator not allowed: {op}"}

            col_sql = quote_ident(col)

            if op == "IN":
                if not isinstance(val, list) or len(val) == 0:
                    return {"ok": False, "error": "IN operator requires a non-empty list value"}
                in_list = ", ".join(format_value(x) for x in val)
                where_clauses.append(f"{col_sql} IN ({in_list})")
            elif op == "LIKE":
                if not isinstance(val, str):
                    return {"ok": False, "error": "LIKE requires a string value"}
                where_clauses.append(f"{col_sql} LIKE {format_value(val)}")
            else:
                where_clauses.append(f"{col_sql} {op} {format_value(val)}")

    order_sql = ""
    if order_by:
        try:
            validate_column(table, order_by)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if order_dir not in {"ASC", "DESC"}:
            return {"ok": False, "error": "order_dir must be ASC or DESC"}
        order_sql = f"\nORDER BY {quote_ident(order_by)} {order_dir}"

    sql = f"SELECT {', '.join(select_cols)}\nFROM {quote_ident(table)}"
    if where_clauses:
        sql += "\nWHERE " + " AND ".join(where_clauses)
    sql += order_sql
    sql += f"\nLIMIT {limit};"

    return execute_sql(sql)


# -----------------------------
# Updates / Inserts for your schema
# -----------------------------

@tool("update_card_credit_limit")
def update_card_credit_limit(
    card_id: int,
    old_limit: Decimal,
    new_limit: Decimal,
) -> Dict[str, Any]:
    """
    Build SQL to update a card's credit limit with optimistic concurrency.
    Table: cards
    Columns: card_id, credit_limit
    """
    if not isinstance(card_id, int) or card_id <= 0:
        return {"ok": False, "error": "card_id must be a positive integer."}

    try:
        old_l = Decimal(old_limit)
        new_l = Decimal(new_limit)
    except Exception:
        return {"ok": False, "error": "old_limit and new_limit must be numeric (Decimal-compatible)."}

    if new_l <= 0:
        return {"ok": False, "error": "new_limit must be positive."}

    sql = (
        "UPDATE cards\n"
        f"SET credit_limit = {format_value(new_l)}\n"
        f"WHERE card_id = {format_value(card_id)}\n"
        f"  AND credit_limit = {format_value(old_l)};"
    )

    return execute_sql(sql)


@tool("update_card_type")
def update_card_type(
    card_id: int,
    new_card_type: str,
) -> Dict[str, Any]:
    """
    Build SQL to update card_type for a card.
    Table: cards
    Columns: card_id, card_type
    """
    if not isinstance(card_id, int) or card_id <= 0:
        return {"ok": False, "error": "card_id must be a positive integer."}
    if not new_card_type or not new_card_type.strip():
        return {"ok": False, "error": "new_card_type is required."}

    sql = (
        "UPDATE cards\n"
        f"SET card_type = {format_value(new_card_type.strip())}\n"
        f"WHERE card_id = {format_value(card_id)};"
    )
    return execute_sql(sql)


@tool("create_customer")
def create_customer(
    first_name: str,
    last_name: str,
    email: str,
) -> Dict[str, Any]:
    """
    Build SQL to insert into customers.
    created_at is assumed to be defaulted by DB (recommended) or you can add NOW().
    """
    if not first_name or not first_name.strip():
        return {"ok": False, "error": "first_name is required."}
    if not last_name or not last_name.strip():
        return {"ok": False, "error": "last_name is required."}
    if not email or not email.strip():
        return {"ok": False, "error": "email is required."}

    sql = (
        "INSERT INTO customers (first_name, last_name, email)\n"
        f"VALUES ({format_value(first_name.strip())}, {format_value(last_name.strip())}, {format_value(email.strip())})\n"
        "RETURNING customer_id;"
    )
    return execute_sql(sql)


@tool("create_card")
def create_card(
    customer_id: int,
    card_number: str,
    card_type: str,
    credit_limit: Decimal,
    issued_date: date,
) -> Dict[str, Any]:
    """
    Build SQL to insert into cards.
    """
    if not isinstance(customer_id, int) or customer_id <= 0:
        return {"ok": False, "error": "customer_id must be a positive integer."}
    if not card_number or not card_number.strip():
        return {"ok": False, "error": "card_number is required."}
    if not card_type or not card_type.strip():
        return {"ok": False, "error": "card_type is required."}

    try:
        cl = Decimal(credit_limit)
    except Exception:
        return {"ok": False, "error": "credit_limit must be numeric (Decimal-compatible)."}
    if cl <= 0:
        return {"ok": False, "error": "credit_limit must be positive."}
    if not isinstance(issued_date, date):
        return {"ok": False, "error": "issued_date must be a Python date."}

    sql = (
        "INSERT INTO cards (customer_id, card_number, card_type, credit_limit, issued_date)\n"
        f"VALUES ({format_value(customer_id)}, {format_value(card_number.strip())}, {format_value(card_type.strip())}, "
        f"{format_value(cl)}, {format_value(issued_date)})\n"
        "RETURNING card_id;"
    )
    return execute_sql(sql)


@tool("create_expense")
def create_expense(
    card_id: int,
    amount: Decimal,
    category: str,
    expense_date: date,
) -> Dict[str, Any]:
    """
    Build SQL to insert into expenses.
    """
    if not isinstance(card_id, int) or card_id <= 0:
        return {"ok": False, "error": "card_id must be a positive integer."}
    try:
        amt = Decimal(amount)
    except Exception:
        return {"ok": False, "error": "amount must be numeric (Decimal-compatible)."}
    if amt <= 0:
        return {"ok": False, "error": "amount must be positive."}
    if not category or not category.strip():
        return {"ok": False, "error": "category is required."}
    if not isinstance(expense_date, date):
        return {"ok": False, "error": "expense_date must be a Python date."}

    sql = (
        "INSERT INTO expenses (card_id, amount, category, expense_date)\n"
        f"VALUES ({format_value(card_id)}, {format_value(amt)}, {format_value(category.strip())}, {format_value(expense_date)})\n"
        "RETURNING expense_id;"
    )
    return execute_sql(sql)


# -----------------------------
# “Business” helpers (joins) – very useful for agents
# -----------------------------

@tool("get_customer_cards")
def get_customer_cards(customer_id: int, limit: int = 50) -> Dict[str, Any]:
    """
    Fetch all cards for a customer.
    """
    if not isinstance(customer_id, int) or customer_id <= 0:
        return {"ok": False, "error": "customer_id must be a positive integer."}
    if not isinstance(limit, int) or limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be 1..500"}

    sql = (
        "SELECT card_id, customer_id, card_number, card_type, credit_limit, issued_date\n"
        "FROM cards\n"
        f"WHERE customer_id = {format_value(customer_id)}\n"
        "ORDER BY issued_date DESC\n"
        f"LIMIT {limit};"
    )
    return execute_sql(sql)


@tool("get_card_expenses")
def get_card_expenses(
    card_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Fetch expenses for a card with optional filters.
    """
    if not isinstance(card_id, int) or card_id <= 0:
        return {"ok": False, "error": "card_id must be a positive integer."}
    if not isinstance(limit, int) or limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be 1..500"}

    where = [f"e.card_id = {format_value(card_id)}"]

    if start_date:
        if not isinstance(start_date, date):
            return {"ok": False, "error": "start_date must be a Python date."}
        where.append(f"e.expense_date >= {format_value(start_date)}")

    if end_date:
        if not isinstance(end_date, date):
            return {"ok": False, "error": "end_date must be a Python date."}
        where.append(f"e.expense_date <= {format_value(end_date)}")

    if category:
        where.append(f"e.category = {format_value(category.strip())}")

    sql = (
        "SELECT e.expense_id, e.card_id, e.amount, e.category, e.expense_date\n"
        "FROM expenses e\n"
        "WHERE " + " AND ".join(where) + "\n"
        "ORDER BY e.expense_date DESC\n"
        f"LIMIT {limit};"
    )
    return execute_sql(sql)


@tool("get_customer_summary")
def get_customer_summary(customer_id: int) -> Dict[str, Any]:
    """
    Single query summary:
    - customer details
    - card list
    - total spend per card
    """
    if not isinstance(customer_id, int) or customer_id <= 0:
        return {"ok": False, "error": "customer_id must be a positive integer."}

    sql = (
        "SELECT\n"
        "  c.customer_id,\n"
        "  c.first_name,\n"
        "  c.last_name,\n"
        "  c.email,\n"
        "  c.created_at,\n"
        "  ca.card_id,\n"
        "  ca.card_number,\n"
        "  ca.card_type,\n"
        "  ca.credit_limit,\n"
        "  ca.issued_date,\n"
        "  COALESCE(SUM(e.amount), 0) AS total_spend\n"
        "FROM customers c\n"
        "LEFT JOIN cards ca ON ca.customer_id = c.customer_id\n"
        "LEFT JOIN expenses e ON e.card_id = ca.card_id\n"
        f"WHERE c.customer_id = {format_value(customer_id)}\n"
        "GROUP BY c.customer_id, ca.card_id\n"
        "ORDER BY ca.issued_date DESC NULLS LAST;"
    )
    return execute_sql(sql)


def execute_sql(sql: str) -> Dict[str, Any]:
    """
    Execute a single allowed SQL statement against Postgres.

    Allowed:
      - SELECT / INSERT / UPDATE / DELETE
      - Only tables: customers, cards, expenses
      - Single statement only
      - Blocks DDL like DROP/ALTER/TRUNCATE/CREATE etc.

    Returns:
      - For SELECT or RETURNING: {"ok": True, "rows": [...], "rowcount": N}
      - For writes w/o returning: {"ok": True, "rowcount": N}
    """
    return run_sql(sql)