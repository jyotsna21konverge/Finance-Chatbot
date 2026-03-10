# Query Examples - What Works Now

## Invoice Distribution Queries

### ✅ "Show the distribution of total invoice amount for all the vendors"
**What happens:**
- Calls `get_vendor_invoice_totals()`
- Creates bar chart visualization
- Shows vendor names vs total amounts

### ✅ "Which vendors have the highest total invoice amounts?"
**What happens:**
- Calls `get_vendor_invoice_totals()`
- Data is already sorted by total (descending)
- Shows top vendors with amounts

### ✅ "Compare total invoices across all vendors"
**What happens:**
- Calls `get_vendor_invoice_totals()`
- Creates comparison visualization
- Shows all vendors side by side

### ✅ "What's the average invoice amount per vendor?"
**What happens:**
- Calls `get_vendor_invoice_totals()`
- Returns average_invoice_amount field
- Can visualize or list in table

## AR Aging Queries

### ✅ "Show me AR aging breakdown"
**What happens:**
- Calls `get_ar_aging_report()`
- Creates bar chart with aging buckets
- Shows Current, 30+, 60+, 90+ days

### ✅ "What's overdue for vendor TechSupply?"
**What happens:**
- Calls `get_vendor_ar_balance("vend_001")`
- Shows aging breakdown for that vendor
- Highlights overdue amounts

## Invoice Listing Queries

### ✅ "List all overdue invoices"
**What happens:**
- Calls `get_overdue_invoices()`
- Creates table visualization
- Shows invoice details

### ✅ "Show invoices for vendor V001"
**What happens:**
- Calls `get_vendor_invoices("vend_001")`
- Creates table with invoice list
- Includes amounts, dates, status

## Vendor Profile Queries

### ✅ "Get vendor profile for TechSupply"
**What happens:**
- Calls `search_vendors("vendor_name", "TechSupply")`
- Shows vendor details in table
- Includes contact, terms, rating

### ✅ "Show me at-risk vendors"
**What happens:**
- Calls `get_at_risk_vendors()`
- Lists vendors with risk factors
- Shows overdue amounts and issues

## Credit & Terms Queries

### ✅ "What's the credit utilization across vendors?"
**What happens:**
- Calls `get_all_vendor_credit_terms()`
- Shows credit limits vs used amounts
- Calculates utilization percentages

### ✅ "Show credit terms for vendor V002"
**What happens:**
- Calls `get_vendor_credit_terms("vend_002")`
- Shows limit, used, available
- Displays utilization percentage

## Summary & Analysis Queries

### ✅ "Give me a complete AR overview"
**What happens:**
- Calls multiple tools (summary, aging, at-risk)
- Creates multiple visualizations
- Shows comprehensive dashboard

### ✅ "What are the key AR metrics?"
**What happens:**
- Calls `get_ar_summary()`
- Shows metrics display
- Includes totals, counts, percentages

## Pie Chart Queries (Proportions & Percentages)

### ✅ "What percentage of invoices are overdue?"
**What happens:**
- Calls `search_invoices()`
- Groups by status
- Creates pie chart showing status distribution
- Shows Current, Overdue, Paid proportions

### ✅ "Show the breakdown of invoices by category"
**What happens:**
- Calls `search_invoices()`
- Groups by invoice_category
- Creates pie chart with categories
- Shows IT Equipment, Services, Raw Materials, etc.

### ✅ "How are payments distributed across payment methods?"
**What happens:**
- Calls `search_invoices()`
- Groups by payment_method
- Creates pie chart showing ACH, Wire Transfer, Credit Card distribution

### ✅ "What's the composition of AR by aging bucket?"
**What happens:**
- Calls `get_ar_aging_report()`
- Calculates totals per bucket
- Creates pie chart showing Current, 30+, 60+, 90+ proportions

### ✅ "Show the proportion of vendors by credit rating"
**What happens:**
- Calls `search_vendors()` or profiles
- Groups by credit_rating
- Creates pie chart showing A, B, C rating distribution

## Dispute Queries

### ✅ "Show all payment disputes"
**What happens:**
- Calls `get_ar_disputes()`
- Lists disputes with details
- Shows amounts and status

### ✅ "Are there any critical payment issues?"
**What happens:**
- Calls `get_critical_payment_issues()`
- Shows escalated issues
- Highlights urgent items

## Tips for Best Results

1. **Be Specific:** Include vendor names or IDs when asking about specific vendors
2. **Use Keywords:** Words like "distribution", "breakdown", "list", "show" help the agent understand intent
3. **Ask Follow-ups:** After getting results, ask for more details or different views
4. **Request Visualizations:** Say "show as chart" or "visualize" to get graphical output
5. **Combine Queries:** Ask for multiple things like "show totals and create a chart"

## Query Patterns That Work Well

- "Show [metric] for [entity]"
- "What's the [analysis] across [group]?"
- "List all [items] where [condition]"
- "Compare [metric] between [entities]"
- "Give me [summary] of [area]"

## Common Issues

### ❌ Vague queries
"Tell me about invoices" → Too broad, be more specific

### ✅ Better version
"Show all overdue invoices" or "What's the total invoice amount by vendor?"

### ❌ Non-existent data
"Show invoices for vendor XYZ123" → If vendor doesn't exist, will return error

### ✅ Better version
"Search for vendors in the Manufacturing industry" → Then use actual vendor IDs

### ❌ Outside scope
"What's the weather today?" → Not related to AR data

### ✅ Better version
Stick to AR, invoices, vendors, payments, credit, disputes
