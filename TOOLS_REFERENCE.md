# JSON Tools - Quick Reference Guide

## Tools by Category

### 👤 Profile/User Tools
| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_user_profile` | `employee_id` | Single user profile |
| `search_users` | `search_field, search_value` | List of matching users |

### 💰 Balance Tools
| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_account_balance` | `account_id` OR `employee_id` | Balance(s) |
| `get_card_balance` | `card_id` | Card balance details |

### 💳 Transaction Tools
| Tool | Parameters | Returns |
|------|-----------|---------|
| `search_transactions` | `card_id`, `employee_id`, `status`, `limit` | Transaction list |
| `get_transaction_by_merchant` | `merchant_name`, `limit` | Merchant transactions |
| `get_denied_transactions` | `employee_id`, `limit` | Denied tx only |

### 📊 Credit Limit Tools
| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_credit_limits` | `employee_id`, `limit` | Credit limit info |
| `get_card_credit_limit` | `card_id` | Single card limit |
| `update_credit_limit` | `card_id, new_limit, reason` | Update confirmation |

### ⚠️ Fraud Alert Tools
| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_fraud_alerts` | `card_id`, `investigation_status`, `limit` | Alert list |
| `get_fraud_alerts_by_employee` | `employee_id`, `limit` | Employee alerts |

### 🚗 Fleet/Fuel Tools
| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_fleet_data` | `vehicle_id`, `limit` | Vehicle list |
| `get_fleet_by_driver` | `driver_id` | Driver's vehicles |
| `search_fleet` | `search_field, search_value` | Matching vehicles |

### 📋 Composite Tools
| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_employee_summary` | `employee_id` | Complete employee profile |
| `get_high_risk_employees` | (none) | Risk-flagged employees |

## Parameter Guide

### Filter Types
- **status**: `"approved"`, `"denied"`, `"pending"`
- **investigation_status**: `"investigating"`, `"resolved"`, `"false_positive"`
- **limit**: 1-500 (default varies)

### Search Fields Examples
**Users:** `name`, `email`, `role`, `department`, `persona`
**Fleet:** `make`, `model`, `driver_name`, `department`, `status`
**Others:** Any field in the JSON objects

## Common Queries

### Get Employee Info
```
get_employee_summary("emp_002")
```

### Find Suspicious Activity
```
get_fraud_alerts_by_employee("emp_004")
```

### Check Credit Status
```
get_card_credit_limit("card_001")
```

### View Recent Transactions
```
search_transactions(employee_id="emp_002", limit=20)
```

### Monitor Fleet
```
search_fleet(search_field="status", search_value="active")
```

### Risk Analysis
```
get_high_risk_employees()
```

## Response Format
All tools return:
```json
{
  "ok": true/false,
  "data": [...],
  "count": N,
  "error": "message (if ok=false)"
}
```
