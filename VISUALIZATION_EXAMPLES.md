# Visualization Examples - Agent-Driven Chart Selection

## How the Agent Decides Chart Types

### Example 1: AR Aging Analysis
**User Query**: "Show me the AR aging breakdown"

**Agent Process**:
1. Calls `get_ar_aging_report()` to retrieve aging data
2. Analyzes data structure: has buckets (Current, 30+, 60+, 90+ days) with amounts
3. Determines: Comparison across categories → Bar chart is best
4. Calls:
```python
create_visualization(
    chart_type="bar",
    title="AR Aging Breakdown",
    data_source="get_ar_aging_report",
    x_field="Status",
    y_field="Amount",
    description="Accounts receivable aging across different time buckets"
)
```

**Result**: Bar chart showing amounts in each aging bucket

---

### Example 2: Invoice Status Distribution
**User Query**: "What's the distribution of invoice statuses?"

**Agent Process**:
1. Calls `search_invoices()` to get all invoices
2. Analyzes: Multiple invoices with status field (paid, overdue, current)
3. Determines: Proportional breakdown → Pie/Bar chart
4. Calls:
```python
create_visualization(
    chart_type="pie",
    title="Invoice Status Distribution",
    data_source="search_invoices",
    x_field="status",
    y_field="count",
    description="Percentage breakdown of invoices by status"
)
```

**Result**: Pie chart (rendered as bar in Streamlit) showing status proportions

---

### Example 3: Vendor Details
**User Query**: "Show me details for vendor V001"

**Agent Process**:
1. Calls `get_vendor_summary("V001")` to get comprehensive data
2. Analyzes: Detailed record with many fields
3. Determines: Detailed information → Table is best
4. Calls:
```python
create_visualization(
    chart_type="table",
    title="Vendor V001 Complete Profile",
    data_source="get_vendor_summary",
    description="Comprehensive vendor information including profile, AR, and credit"
)
```

**Result**: Formatted table with all vendor details

---

### Example 4: Key AR Metrics
**User Query**: "What are the key AR metrics?"

**Agent Process**:
1. Calls `get_ar_summary()` to get overall metrics
2. Analyzes: Aggregate numbers (totals, counts, averages)
3. Determines: Key performance indicators → Metrics display
4. Calls:
```python
create_visualization(
    chart_type="metrics",
    title="Key AR Performance Indicators",
    data_source="get_ar_summary",
    description="Critical AR metrics at a glance"
)
```

**Result**: Metric cards showing Total AR, Overdue Amount, Vendor Count, etc.

---

### Example 5: Credit Utilization vs Overdue
**User Query**: "Is there a correlation between credit utilization and overdue amounts?"

**Agent Process**:
1. Calls `get_all_vendor_credit_terms()` and `get_ar_aging_report()`
2. Analyzes: Two numeric variables to compare
3. Determines: Correlation analysis → Scatter plot
4. Calls:
```python
create_visualization(
    chart_type="scatter",
    title="Credit Utilization vs Overdue Amounts",
    data_source="get_all_vendor_credit_terms",
    x_field="utilization_percent",
    y_field="overdue_amount",
    description="Relationship between credit usage and payment delays"
)
```

**Result**: Scatter plot showing correlation pattern

---

### Example 6: Multiple Visualizations
**User Query**: "Give me a complete AR overview"

**Agent Process**:
1. Calls multiple tools: `get_ar_summary()`, `get_ar_aging_report()`, `get_at_risk_vendors()`
2. Determines: Complex query needs multiple views
3. Calls `create_visualization()` multiple times:

```python
# Visualization 1: Key metrics
create_visualization(
    chart_type="metrics",
    title="AR Summary Metrics",
    data_source="get_ar_summary",
    description="Overall AR performance"
)

# Visualization 2: Aging breakdown
create_visualization(
    chart_type="bar",
    title="AR Aging Analysis",
    data_source="get_ar_aging_report",
    x_field="aging_bucket",
    y_field="amount",
    description="Breakdown by aging period"
)

# Visualization 3: At-risk vendors
create_visualization(
    chart_type="table",
    title="At-Risk Vendors",
    data_source="get_at_risk_vendors",
    description="Vendors requiring immediate attention"
)
```

**Result**: Dashboard with metrics, bar chart, and table

---

## Decision Logic

The agent uses these guidelines to choose chart types:

| Data Characteristics | Recommended Chart | Use Case |
|---------------------|-------------------|----------|
| Categories with values | Bar | Status counts, aging buckets, vendor comparisons |
| Time series data | Line | Payment trends, balance over time |
| Part-to-whole | Pie | Status distribution, category percentages |
| Detailed records | Table | Invoice lists, vendor profiles, transaction history |
| Key numbers | Metrics | Totals, averages, counts, KPIs |
| Two numeric variables | Scatter | Correlations, relationships |

## Testing the Feature

### Test Query 1: Simple Comparison
```
User: "Compare overdue amounts across aging buckets"
Expected: Bar chart with aging buckets on x-axis, amounts on y-axis
```

### Test Query 2: Detailed List
```
User: "List all invoices for TechSupply"
Expected: Table with invoice details
```

### Test Query 3: Summary Metrics
```
User: "What's the total AR and number of vendors?"
Expected: Metrics display with key numbers
```

### Test Query 4: Complex Analysis
```
User: "Analyze AR aging and show at-risk vendors"
Expected: Multiple visualizations (bar chart + table)
```

## Advantages Over Hardcoded Approach

### Before (Hardcoded):
- Fixed logic: "if 'invoice' in tool_name → show table"
- No context awareness
- Can't adapt to query intent
- Requires code changes for new patterns

### After (Agent-Driven):
- Dynamic: Agent analyzes data and context
- Intent-aware: Understands what user wants to see
- Flexible: Can create multiple visualizations
- Extensible: New chart types via prompt updates

## Implementation Notes

1. **Fallback Behavior**: If agent doesn't call `create_visualization`, the system falls back to legacy pattern-matching
2. **Error Handling**: If visualization fails, displays data as table
3. **Data Validation**: Checks if required fields exist before rendering
4. **Multiple Charts**: Agent can recommend multiple visualizations per query
