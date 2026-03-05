# Migration Guide: Database Tools → JSON Tools

## What Changed

Your agent has been migrated from a **database-centric architecture** to a **JSON-centric architecture**. This guide helps you understand the mapping.

## Tool Mapping

### Removed Database Tools

The following SQL-based tools have been **removed and replaced**:

| Old Tool | Purpose | New Replacement(s) |
|----------|---------|-------------------|
| `search_table` | Generic SQL SELECT | `search_transactions`, `search_users`, `search_fleet` |
| `get_customer_cards` | Get cards for customer | `get_card_credit_limit`, `get_card_balance` |
| `get_card_expenses` | Get card transactions | `search_transactions` |
| `get_customer_summary` | Customer overview | `get_employee_summary` |
| `create_customer` | Insert customer | ❌ Not supported (read-only for profiles) |
| `create_card` | Insert card | ❌ Not supported (cards via credit_limits) |
| `create_expense` | Insert transaction | ❌ Not supported (transactions are pre-existing) |
| `update_card_credit_limit` | Update limit | `update_credit_limit` |
| `update_card_type` | Update card type | ❌ Not supported (read-only) |
| `execute_sql` | Raw SQL execution | ❌ Not supported (JSON only) |

## New Tools by Use Case

### 👤 Customer/Employee Information
**Old:** `search_table("customers", ...)`
**New:** 
```python
get_user_profile(employee_id)
search_users(search_field, search_value)
```

### 💰 Balance Information
**Old:** `search_table("cards", ...)` + custom filtering
**New:**
```python
get_account_balance(account_id=None, employee_id=None)
get_card_balance(card_id)
```

### 💳 Transactions/Expenses
**Old:** `get_card_expenses(card_id, ...)`
**New:**
```python
search_transactions(card_id, employee_id, status, limit)
get_transaction_by_merchant(merchant_name, limit)
get_denied_transactions(employee_id, limit)
```

### 📊 Credit Management
**Old:** `update_card_credit_limit(card_id, old_limit, new_limit)`
**New:**
```python
get_credit_limits(employee_id, limit)
get_card_credit_limit(card_id)
update_credit_limit(card_id, new_limit, reason)  # Improved with reason tracking
```

### ⚠️ Fraud & Risk
**Old:** `search_table("fraud_alerts", ...)` (if available)
**New:**
```python
get_fraud_alerts(card_id, investigation_status, limit)
get_fraud_alerts_by_employee(employee_id, limit)
get_high_risk_employees()  # New risk analysis tool
```

### 🚗 Fleet Management
**Old:** Not available in database
**New:**
```python
get_fleet_data(vehicle_id, limit)
get_fleet_by_driver(driver_id)
search_fleet(search_field, search_value)
```

### 📋 Comprehensive Views
**Old:** `get_customer_summary(customer_id)` (limited)
**New:**
```python
get_employee_summary(employee_id)  # Profile + Balances + Transactions + Credits + Fraud + Fleet
```

## Data Access Patterns

### Before (SQL)
```python
# Get customer cards
sql = "SELECT * FROM cards WHERE customer_id = ? LIMIT 50"
result = execute_sql(sql)

# Update credit
sql = "UPDATE cards SET credit_limit = ? WHERE card_id = ? AND credit_limit = ?"
execute_sql(sql)
```

### After (JSON)
```python
# Get card credit limits
result = get_credit_limits(employee_id="emp_001")

# Update credit limit
result = update_credit_limit(card_id="card_001", new_limit=5000)
```

## API Consistency

All new tools return the same response format:
```python
{
    "ok": True,           # Boolean success indicator
    "data": [...],        # Result(s)
    "count": N,           # Number of results
    "error": "msg"        # Error message if ok=False
}
```

**Old database responses varied by tool.**
**New JSON tools are consistent and predictable.**

## Feature Improvements

| Aspect | Old (Database) | New (JSON) |
|--------|---|---|
| **Searching** | Limited to predefined queries | Search any field with any value |
| **Filtering** | SQL WHERE clauses | Simple dictionary-based filters |
| **Performance** | DB network latency | In-memory with caching |
| **Updates** | Complex SQL transactions | Simple JSON persistence |
| **Error Handling** | Database errors | Standardized error responses |
| **Data Types** | Various DB types | Native Python types |
| **Caching** | No built-in caching | Automatic caching |
| **Fleet Data** | Not available | Full fleet management |
| **Fraud Analysis** | Basic alerts | Alerts + Risk scoring |
| **Risk Summary** | Manual analysis needed | Automated high-risk detection |

## What's New

These tools didn't exist in the database version:

1. **`search_users()`** - Search profiles by any field
2. **`get_transaction_by_merchant()`** - Find all merchant transactions
3. **`get_denied_transactions()`** - Specifically for denied transactions
4. **`search_fleet()`** - Search vehicles by any field
5. **`get_fleet_by_driver()`** - Get driver's vehicle assignments
6. **`get_high_risk_employees()`** - Automated risk analysis
7. **Fleet management tools** - Entire new capability

## Data Type Changes

### Customer → Employee
- Database: `customer_id` (integer)
- JSON: `employee_id` (string like "emp_001")

### Transaction Status
- Database: May have been implicit or stored differently
- JSON: Clear statuses: "approved", "denied", "pending"

### Credit Limits
- Database: Single update approach
- JSON: Tracks adjustment history with timestamps and reasons

## Limitations & Workarounds

### Limitation: Can't create new records
**Old:** `create_customer()`, `create_card()`, `create_expense()`
**Why:** Input data is read-only JSON files
**Workaround:** Manually edit JSON files or add data via separate process

### Limitation: Can't delete records
**Why:** Data integrity - JSON is the source of truth
**Workaround:** Mark as inactive/archived in JSON files

### Limitation: Account type changes
**Old:** `update_card_type()`
**Why:** Card type is static in current JSON structure
**Workaround:** Extend JSON schema if needed

## Schema Understanding

### Old Database Schema
- customers table
- cards table  
- expenses table

### New JSON Structure
```
data/
├── profiles.json         # Users
├── balances.json         # Account balances
├── transactions.json     # Expenses/transactions
├── credit_limits.json    # Card credit info
├── fraud_alerts.json     # Fraud detection
└── fleet_fuel.json       # Vehicles
```

## Performance Characteristics

| Operation | Database | JSON |
|-----------|----------|------|
| First Load | Fast (indexed) | Load whole file |
| Cached Access | Network + DB | Memory |
| Search | DB execution | Python filter |
| Update | COMMIT transaction | JSON persistence |
| Complex Joins | Built-in | Manual in code |

## Migration Checklist

- ✅ Old database tools removed
- ✅ New JSON tools implemented
- ✅ Consistent response format
- ✅ Error handling standardized
- ✅ Agent fully configured
- ✅ Documentation provided
- ✅ All data sources supported

## Getting Help

Refer to these files for more details:
- `TOOLS_REFERENCE.md` - Quick lookup of all tools
- `JSON_TOOLS_UPDATE.md` - Detailed documentation
- `IMPLEMENTATION_SUMMARY.md` - Overall changes

---

**Migration Status: ✅ Complete**

Your agent is now JSON-native and ready for production use.
