from typing import Literal

TABLE_NAME = "employees"
ALLOWED_COLUMNS = {
    "employee_id",
    "email",
    "manager_id",
    "status",
    "credit_limit",
    "credit_limit_reason",
}

# Allowed operators to avoid weird SQL
OP = Literal["=", "!=", ">", ">=", "<", "<=", "IN", "LIKE"]

MODEL = "gpt-4o-mini"