# Pie Chart Queries - When and How

## What Makes a Good Pie Chart Query?

Pie charts are ideal for showing:
- **Proportions**: Parts of a whole
- **Percentages**: Relative distribution
- **Composition**: What makes up a total
- **Categories**: Limited number (3-7 categories work best)

## Query Examples That Result in Pie Charts

### 1. Invoice Status Distribution

#### ✅ "What percentage of invoices are overdue?"
**Why pie chart:**
- Shows proportion of overdue vs current vs paid
- Clear visual of status breakdown
- Easy to see which status dominates

**Agent will:**
1. Call `search_invoices()` to get all invoices
2. Count invoices by status
3. Call `create_visualization(chart_type="pie", x_field="status", y_field="count")`

**Result:** Pie chart with slices for:
- Current invoices
- Overdue invoices
- Paid invoices

---

#### ✅ "Show me the distribution of invoice statuses"
**Why pie chart:**
- "Distribution" suggests proportional breakdown
- Status is categorical data
- Want to see relative sizes

**Expected output:** Pie chart showing percentage of each status

---

#### ✅ "What's the breakdown of invoices by payment status?"
**Why pie chart:**
- "Breakdown" indicates composition analysis
- Payment status categories (paid, unpaid, partial)
- Shows what portion is in each state

---

### 2. Invoice Category Analysis

#### ✅ "Show the proportion of invoices by category"
**Why pie chart:**
- "Proportion" is key word for pie charts
- Categories like: IT Equipment, Services, Raw Materials, etc.
- Shows which categories dominate spending

**Agent will:**
1. Call `search_invoices()`
2. Group by invoice_category
3. Create pie chart with categories and amounts

**Result:** Pie chart showing:
- IT Equipment: 25%
- Services: 30%
- Raw Materials: 35%
- Other: 10%

---

#### ✅ "What percentage of our invoices are for services vs products?"
**Why pie chart:**
- Explicitly asks for percentages
- Binary or few categories
- Comparison of proportions

---

### 3. Payment Method Distribution

#### ✅ "How are our payments distributed across payment methods?"
**Why pie chart:**
- Shows composition of payment methods
- Categories: ACH, Wire Transfer, Credit Card
- Visualizes which methods are most used

**Agent will:**
1. Call `search_invoices()`
2. Group by payment_method
3. Count or sum amounts by method
4. Create pie chart

**Result:** Pie chart showing:
- ACH: 45%
- Wire Transfer: 35%
- Credit Card: 20%

---

### 4. Vendor Industry Breakdown

#### ✅ "What's the composition of our vendors by industry?"
**Why pie chart:**
- "Composition" suggests parts of whole
- Industry categories
- Shows diversity of vendor base

**Agent will:**
1. Call `search_vendors()` or get all profiles
2. Group by industry
3. Create pie chart

**Result:** Pie chart showing:
- Manufacturing: 30%
- Technology: 25%
- Services: 20%
- Other: 25%

---

### 5. AR Aging Proportions

#### ✅ "What percentage of AR is in each aging bucket?"
**Why pie chart:**
- Explicitly asks for percentages
- Aging buckets: Current, 30+, 60+, 90+
- Shows risk distribution

**Agent will:**
1. Call `get_ar_aging_report()`
2. Calculate totals for each bucket
3. Create pie chart with percentages

**Result:** Pie chart showing:
- Current: 60%
- 30-60 days: 20%
- 60-90 days: 12%
- 90+ days: 8%

---

### 6. Credit Utilization Categories

#### ✅ "Show the distribution of vendors by credit utilization level"
**Why pie chart:**
- Categorize vendors: Low (<50%), Medium (50-75%), High (>75%)
- Shows risk distribution
- Proportional view of credit health

**Agent will:**
1. Call `get_all_vendor_credit_terms()`
2. Categorize by utilization_percent
3. Create pie chart

**Result:** Pie chart showing:
- Low utilization: 50%
- Medium utilization: 30%
- High utilization: 20%

---

## Key Words That Trigger Pie Charts

When users say these words, the agent should consider pie charts:
- **"percentage"** - "What percentage of..."
- **"proportion"** - "Show the proportion of..."
- **"distribution"** - "Show the distribution of..." (when categorical)
- **"breakdown"** - "Give me a breakdown by..."
- **"composition"** - "What's the composition of..."
- **"split"** - "How is X split between..."
- **"share"** - "What's the share of each..."

## When NOT to Use Pie Charts

### ❌ Too Many Categories
"Show invoice amounts for all 20 vendors"
- Better as bar chart (easier to compare many items)

### ❌ Comparing Absolute Values
"Compare total invoice amounts across vendors"
- Better as bar chart (shows actual amounts, not just proportions)

### ❌ Time Series Data
"Show payment trends over the last 6 months"
- Better as line chart (shows progression)

### ❌ Detailed Records
"List all overdue invoices"
- Better as table (need details, not proportions)

## Implementation Details

### How the Agent Decides

The agent analyzes the query for:
1. **Intent**: Is user asking about proportions/percentages?
2. **Data type**: Is it categorical with limited categories?
3. **Purpose**: Do they want to see parts of a whole?

### Visualization Call Example

```python
create_visualization(
    chart_type="pie",
    title="Invoice Status Distribution",
    data_source="search_invoices",
    x_field="status",  # Category field
    y_field="count",   # Value field (or amount)
    description="Percentage breakdown of invoices by status"
)
```

### Technical Implementation

The pie chart is rendered using Plotly:
- Donut chart style (hole=0.3) for better readability
- Shows percentages and labels inside slices
- Interactive (hover for details)
- Includes data table below for exact values

## Testing Pie Chart Queries

Try these in the Streamlit app:

1. **"What percentage of invoices are overdue?"**
   - Should show pie chart with status distribution

2. **"Show the breakdown of invoices by category"**
   - Should show pie chart with invoice categories

3. **"How are payments distributed across payment methods?"**
   - Should show pie chart with payment methods

4. **"What's the composition of AR by aging bucket?"**
   - Should show pie chart with aging buckets

5. **"Show the proportion of vendors by credit rating"**
   - Should show pie chart with credit ratings

## Customization Tips

To get better pie charts, users can:
- Be specific about what to show: "Show percentage of invoice AMOUNTS by status" vs "Show percentage of invoice COUNT by status"
- Limit categories: "Show top 5 vendors by invoice amount"
- Ask for specific groupings: "Group vendors by credit rating and show distribution"

## Advantages of Pie Charts

✅ **Quick understanding** of proportions
✅ **Visual impact** - easy to see dominant categories
✅ **Percentage focus** - shows relative importance
✅ **Simple message** - "most of X is Y"
✅ **Good for presentations** - clear and professional

## Best Practices

1. **Limit to 5-7 slices** - More becomes hard to read
2. **Use for percentages** - Not absolute comparisons
3. **Ensure categories are mutually exclusive** - No overlap
4. **Order by size** - Largest to smallest (optional)
5. **Include data table** - For exact values
