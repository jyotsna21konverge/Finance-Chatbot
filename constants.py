from typing import Dict, List, Literal, Set

OP = Literal["=", "!=", ">", ">=", "<", "<=", "IN", "LIKE"]

TABLES: Dict[str, Set[str]] = {
    "customers": {
        "customer_id", "first_name", "last_name", "email", "created_at",
    },
    "cards": {
        "card_id", "customer_id", "card_number", "card_type", "credit_limit", "issued_date",
    },
    "expenses": {
        "expense_id", "card_id", "amount", "category", "expense_date",
    },
}

DEFAULT_SELECT: Dict[str, List[str]] = {
    "customers": ["customer_id", "first_name", "last_name", "email", "created_at"],
    "cards": ["card_id", "customer_id", "card_number", "card_type", "credit_limit", "issued_date"],
    "expenses": ["expense_id", "card_id", "amount", "category", "expense_date"],
}

ALLOWED_TABLES = tuple(TABLES.keys())  # ("customers", "cards", "expenses")

MODEL = "gpt-4o-mini"