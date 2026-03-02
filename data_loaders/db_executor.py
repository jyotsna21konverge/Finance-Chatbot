from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extras

from dataconnectors.data_connector import DataConnector

ALLOWED_TABLES = {"customers", "cards", "expenses"}

# Block obvious destructive/DDL ops. (You can expand this list.)
BLOCKED = {
    "drop", "alter", "truncate", "create", "grant", "revoke",
    "vacuum", "analyze", "comment", "reindex",
}

# Only allow these statement types
ALLOWED_PREFIXES = ("select", "insert", "update", "delete")


def _normalize_sql(sql: str) -> str:
    # collapse whitespace to simplify checks (do not change quoted strings perfectly, but good enough here)
    return re.sub(r"\s+", " ", sql.strip())


def _is_single_statement(sql: str) -> bool:
    # disallow multiple statements; allow a single trailing semicolon
    s = sql.strip()
    if s.count(";") == 0:
        return True
    if s.endswith(";") and s[:-1].count(";") == 0:
        return True
    return False


def _extract_tables(sql_norm: str) -> List[str]:
    """
    Very lightweight table reference extraction.
    Works for simple queries and most generated SQL.
    """
    # matches FROM <table>, JOIN <table>, UPDATE <table>, INTO <table>, DELETE FROM <table>
    patterns = [
        r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
        r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
        r"\bupdate\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
        r"\binsert\s+into\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
        r"\bdelete\s+from\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
    ]
    tables: List[str] = []
    for pat in patterns:
        for m in re.finditer(pat, sql_norm, flags=re.IGNORECASE):
            tables.append(m.group(1).lower())
    # dedupe while preserving order
    seen = set()
    out = []
    for t in tables:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
    if not sql or not sql.strip():
        return False, "SQL is empty."

    if not _is_single_statement(sql):
        return False, "Only single-statement SQL is allowed."

    sql_norm = _normalize_sql(sql).lower()

    # allow optional leading WITH ... SELECT/UPDATE/DELETE/INSERT checks:
    # If starts with WITH, later must contain one of allowed prefixes.
    if sql_norm.startswith("with "):
        if not any(re.search(rf"\b{p}\b", sql_norm) for p in ALLOWED_PREFIXES):
            return False, "CTE SQL must contain SELECT/INSERT/UPDATE/DELETE."
    else:
        if not sql_norm.startswith(ALLOWED_PREFIXES):
            return False, f"Only {', '.join(ALLOWED_PREFIXES)} are allowed."

    # block DDL/destructive keywords anywhere
    for kw in BLOCKED:
        if re.search(rf"\b{re.escape(kw)}\b", sql_norm):
            return False, f"Blocked keyword found: {kw}"

    # ensure only allowed tables are referenced
    tables = _extract_tables(sql_norm)
    for t in tables:
        if t not in ALLOWED_TABLES:
            return False, f"Table not allowed: {t}. Allowed: {sorted(ALLOWED_TABLES)}"

    return True, None


def get_pg_conn() -> psycopg2.extensions.connection:
    """
    Uses env vars so you don't hardcode secrets:
      PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
    """
    host = os.getenv("PG_HOST", "localhost")
    port = int(os.getenv("PG_PORT", "5432"))
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "")
    db = os.getenv("PG_DB", "postgres")

    dc = DataConnector()
    conn = dc.connect_postgres(host=host, port=port, user=user, password=password, db_name=db)
    if conn is None:
        raise RuntimeError("Failed to connect to Postgres (DataConnector returned None).")
    return conn


def run_sql(sql: str) -> Dict[str, Any]:
    """
    Executes allowed SQL safely-ish:
    - SELECT returns rows
    - INSERT/UPDATE/DELETE returns rowcount and optional RETURNING rows
    """
    ok, err = validate_sql(sql)
    if not ok:
        return {"ok": False, "error": err}

    conn = None
    try:
        conn = get_pg_conn()
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)

                # If it's a SELECT or has RETURNING, fetch rows
                if cur.description is not None:
                    rows = cur.fetchall()
                    return {"ok": True, "rows": rows, "rowcount": cur.rowcount}

                # otherwise no rows
                return {"ok": True, "rowcount": cur.rowcount}

    except Exception as e:
        # rollback handled by "with conn:" block if exception occurs
        return {"ok": False, "error": str(e)}
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass