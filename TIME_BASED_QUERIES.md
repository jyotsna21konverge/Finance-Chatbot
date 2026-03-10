# Time-Based Query Support

## Overview
The AR Agent now supports time-based queries to analyze invoices and vendor activity within specific time periods.

## New Tools Added

### 1. `get_recent_invoices`
**Purpose:** Get invoices created within the last N days

**Parameters:**
- `days_back`: Number of days to look back (default 30)

**Returns:**
- invoice_id, vendor_name, vendor_id
- invoice_date, due_date
- invoice_amount, amount_due (outstanding)
- status, payment_status
- days_since_invoice: How many days ago the invoice was created

**Example Use:**
```python
get_recent_invoices(days_back=30)  # Last 30 days
get_recent_invoices(days_back=7)   # Last 7 days
```

---

### 2. `get_vendor_outstanding_by_period`
**Purpose:** Get vendors who raised invoices in the last N days with their total outstanding amounts

**Parameters:**
- `days_back`: Number of days to look back (default 30)

**Returns:**
- vendor_id, vendor_name
- invoice_count: Number of invoices in the period
- total_invoice_amount: Total amount of invoices in period
- total_outstanding_amount: Total amount still due
- average_days_outstanding: Average days since invoice
- invoices: List of invoices in the period

**Perfect For:**
- "List all vendors which raised invoices in last 1 month"
- "Show vendors with invoices in the last 30 days and their outstanding amounts"
- "Which vendors have recent invoices?"

**Example Use:**
```python
get_vendor_outstanding_by_period(days_back=30)  # Last month
get_vendor_outstanding_by_period(days_back=90)  # Last quarter
```

---

### 3. `get_invoices_by_date_range`
**Purpose:** Get invoices within a specific date range

**Parameters:**
- `start_date`: Start date in format "YYYY-MM-DD" (e.g., "2026-02-01")
- `end_date`: End date in format "YYYY-MM-DD" (e.g., "2026-03-10")

**Returns:**
- invoice_id, vendor_name, vendor_id
- invoice_date, due_date
- invoice_amount, amount_due
- status, payment_status

**Perfect For:**
- "Show invoices between Feb 1 and Mar 10"
- "Get all invoices from Q1 2026"
- "List invoices created in February"

**Example Use:**
```python
get_invoices_by_date_range("2026-02-01", "2026-03-10")
get_invoices_by_date_range("2026-01-01", "2026-03-31")
```

---

## Query Examples

### Example 1: Last Month Vendors
**Query:** "List all vendors which raised invoices in last 1 month and their total outstanding amount"

**Agent Process:**
1. Calls `get_vendor_outstanding_by_period(days_back=30)`
2. Gets vendors with invoices in last 30 days
3. Calls `create_visualization(chart_type="bar", ...)` to show vendor comparison
4. Provides text summary with vendor names and outstanding amounts

**Expected Output:**
- Bar chart showing vendors by outstanding amount
- Table with vendor details
- Text summary: "5 vendors raised invoices in the last month with total outstanding of $XXX"

---

### Example 2: Recent Invoices
**Query:** "Show me all invoices created in the last 2 weeks"

**Agent Process:**
1. Calls `get_recent_invoices(days_back=14)`
2. Gets all invoices from last 14 days
3. Calls `create_visualization(chart_type="table", ...)` for detailed list
4. Provides summary with invoice count and total amounts

**Expected Output:**
- Table with invoice details
- Summary: "12 invoices created in the last 2 weeks totaling $XXX"

---

### Example 3: Date Range Analysis
**Query:** "What invoices were created between February 1 and March 10, 2026?"

**Agent Process:**
1. Calls `get_invoices_by_date_range("2026-02-01", "2026-03-10")`
2. Gets invoices in that date range
3. Calls `create_visualization(chart_type="table", ...)` for list
4. Provides summary with count and totals

**Expected Output:**
- Table with invoices in date range
- Summary: "25 invoices created between Feb 1 and Mar 10"

---

## How the Agent Interprets Time Phrases

The agent understands these time-based phrases:

| Phrase | Interpretation | Tool Used |
|--------|-----------------|-----------|
| "last 1 month" | Last 30 days | `get_vendor_outstanding_by_period(30)` |
| "last month" | Last 30 days | `get_vendor_outstanding_by_period(30)` |
| "last 2 weeks" | Last 14 days | `get_recent_invoices(14)` |
| "last 7 days" | Last 7 days | `get_recent_invoices(7)` |
| "recent invoices" | Last 30 days | `get_recent_invoices(30)` |
| "between X and Y" | Date range | `get_invoices_by_date_range(X, Y)` |
| "from X to Y" | Date range | `get_invoices_by_date_range(X, Y)` |

---

## Data Structure

### Recent Invoices Output
```python
{
    "ok": True,
    "days_back": 30,
    "count": 15,
    "data": [
        {
            "invoice_id": "INV-2026-001",
            "vendor_id": "vend_001",
            "vendor_name": "TechSupply Solutions",
            "invoice_date": "2026-02-10T00:00:00Z",
            "due_date": "2026-03-12T00:00:00Z",
            "invoice_amount": 12000.00,
            "amount_due": 12000.00,
            "status": "current",
            "payment_status": "unpaid",
            "days_since_invoice": 28
        },
        # ... more invoices
    ]
}
```

### Vendor Outstanding by Period Output
```python
{
    "ok": True,
    "days_back": 30,
    "vendor_count": 5,
    "data": [
        {
            "vendor_id": "vend_001",
            "vendor_name": "TechSupply Solutions",
            "invoice_count": 4,
            "total_invoice_amount": 67000.00,
            "total_outstanding_amount": 67000.00,
            "average_days_outstanding": 28.5,
            "invoices": [
                {
                    "invoice_id": "INV-2026-001",
                    "invoice_amount": 12000.00,
                    "amount_due": 12000.00,
                    "status": "current",
                    "days_since": 28
                },
                # ... more invoices
            ]
        },
        # ... more vendors
    ]
}
```

---

## Visualization Support

Time-based queries automatically generate appropriate visualizations:

### For Vendor Outstanding by Period:
- **Chart Type:** Bar chart (vendor comparison)
- **X-axis:** Vendor names
- **Y-axis:** Total outstanding amount
- **Also shows:** Data table with details

### For Recent Invoices:
- **Chart Type:** Table (detailed records)
- **Shows:** All invoice details
- **Sortable:** By date, vendor, amount, status

### For Date Range:
- **Chart Type:** Table or Bar chart
- **Depends on:** Number of invoices and query intent

---

## Testing

Run the test script to verify time-based queries work:

```bash
python test_time_based_queries.py
```

This will test:
1. Last month vendor query
2. Date range query
3. Verify tool calls and visualizations

---

## System Prompt Updates

The system prompt now includes:

```
10. For time-based queries (last month, recent invoices, etc.):
    - Use get_vendor_outstanding_by_period for "vendors with invoices in last X days and their outstanding amounts"
    - Use get_recent_invoices for "invoices created in the last X days"
    - Use get_invoices_by_date_range for specific date ranges like "between Feb 1 and Mar 10"
```

This guides the agent to use the appropriate tool for each query type.

---

## Limitations & Notes

1. **Date Format:** Dates must be in "YYYY-MM-DD" format for date range queries
2. **Timezone:** All dates are treated as UTC (Z timezone)
3. **Days Back:** Limited to 1-365 days for safety
4. **Performance:** Queries scan all invoices (up to 1000) for efficiency

---

## Future Enhancements

Potential improvements:
1. Support for relative dates ("this month", "this quarter")
2. Trend analysis over multiple periods
3. Forecasting based on historical patterns
4. Comparison between time periods
5. Custom date range presets

---

## Summary

The agent can now answer time-based queries like:
- ✅ "List all vendors which raised invoices in last 1 month and their outstanding amounts"
- ✅ "Show me invoices from the last 2 weeks"
- ✅ "What invoices were created between Feb 1 and Mar 10?"
- ✅ "Which vendors have recent activity?"
- ✅ "Show invoices created in the last 7 days"

All with automatic visualization and detailed analysis!
