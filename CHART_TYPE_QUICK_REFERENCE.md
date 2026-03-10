# Chart Type Quick Reference

## When to Use Each Chart Type

### 📊 Bar Chart
**Best for:** Comparisons, rankings, distributions with absolute values

**Use when:**
- Comparing amounts across categories
- Showing rankings (top vendors, highest amounts)
- Displaying distributions with many items
- Need to see exact values easily

**Example queries:**
- "Show total invoice amounts by vendor"
- "Compare AR aging buckets"
- "Which vendors have the most overdue invoices?"
- "Rank vendors by total spending"

**Keywords:** compare, rank, top, highest, most, total, amount

---

### 🥧 Pie Chart
**Best for:** Proportions, percentages, composition

**Use when:**
- Showing parts of a whole
- Displaying percentages
- 3-7 categories maximum
- Want to emphasize relative sizes

**Example queries:**
- "What percentage of invoices are overdue?"
- "Show the breakdown of invoices by category"
- "How are payments distributed across payment methods?"
- "What's the composition of AR by aging bucket?"

**Keywords:** percentage, proportion, distribution, breakdown, composition, split, share

---

### 📈 Line Chart
**Best for:** Trends over time, progression

**Use when:**
- Showing changes over time
- Displaying trends
- Tracking progression
- Comparing time series

**Example queries:**
- "Show payment trends over the last 6 months"
- "How has AR balance changed over time?"
- "Track vendor payment history"
- "Show invoice volume by month"

**Keywords:** trend, over time, history, progression, change, monthly, weekly

---

### 📋 Table
**Best for:** Detailed records, lists, exact values

**Use when:**
- Need to see all details
- Listing individual records
- Showing multiple fields per item
- Exact values are important

**Example queries:**
- "List all overdue invoices"
- "Show vendor details for TechSupply"
- "Display all invoices for vendor V001"
- "Show me the complete vendor profile"

**Keywords:** list, show details, display, all, complete, full

---

### 📊 Metrics
**Best for:** Key numbers, KPIs, summary statistics

**Use when:**
- Showing totals, averages, counts
- Displaying KPIs
- Summary statistics
- Dashboard-style overview

**Example queries:**
- "What are the key AR metrics?"
- "Show total AR and overdue amounts"
- "How many vendors do we have?"
- "What's the average invoice amount?"

**Keywords:** total, average, count, sum, key metrics, KPI

---

### 🔵 Scatter Plot
**Best for:** Correlations, relationships between variables

**Use when:**
- Showing correlation between two variables
- Identifying patterns or clusters
- Analyzing relationships
- Detecting outliers

**Example queries:**
- "Is there a correlation between credit utilization and overdue amounts?"
- "Show relationship between invoice amount and days overdue"
- "Plot credit limit vs AR balance"
- "Analyze vendor size vs payment delays"

**Keywords:** correlation, relationship, vs, compared to, pattern

---

## Decision Tree

```
Is it about time/dates?
├─ YES → Line Chart
└─ NO ↓

Is it showing proportions/percentages?
├─ YES → Pie Chart
└─ NO ↓

Is it comparing values across categories?
├─ YES → Bar Chart
└─ NO ↓

Is it showing correlation between two variables?
├─ YES → Scatter Plot
└─ NO ↓

Is it a single number or few key metrics?
├─ YES → Metrics
└─ NO ↓

Need detailed records?
└─ YES → Table
```

## Quick Examples by Query Type

### "Show me..." queries
- "Show me totals" → Metrics
- "Show me trends" → Line Chart
- "Show me breakdown" → Pie Chart
- "Show me comparison" → Bar Chart
- "Show me details" → Table

### "What..." queries
- "What percentage..." → Pie Chart
- "What are the totals..." → Metrics
- "What's the trend..." → Line Chart
- "What are the top..." → Bar Chart

### "How..." queries
- "How are X distributed..." → Pie Chart
- "How does X compare to Y..." → Bar Chart or Scatter
- "How has X changed..." → Line Chart
- "How many..." → Metrics

### "List..." queries
- "List all..." → Table
- "List top..." → Bar Chart or Table

## Common Combinations

Some queries benefit from multiple visualizations:

**"Give me a complete AR overview"**
- Metrics (totals, counts)
- Bar Chart (aging breakdown)
- Table (at-risk vendors)

**"Analyze vendor payment patterns"**
- Line Chart (payment history)
- Bar Chart (vendor comparison)
- Metrics (summary stats)

**"Show invoice status analysis"**
- Pie Chart (status distribution)
- Bar Chart (amounts by status)
- Table (overdue invoice list)

## Tips for Users

1. **Be specific about what you want:**
   - "Show percentage" → Pie Chart
   - "Show amounts" → Bar Chart
   - "Show trend" → Line Chart

2. **Use the right keywords:**
   - Proportion words → Pie
   - Comparison words → Bar
   - Time words → Line

3. **Ask for what you need:**
   - Need exact values? → Ask for table
   - Need visual impact? → Ask for chart
   - Need both? → Agent will provide both

4. **Follow up questions work well:**
   - First: "Show AR summary" (gets metrics)
   - Then: "Break that down by aging bucket" (gets bar chart)
   - Then: "What percentage is overdue?" (gets pie chart)

## Agent Intelligence

The agent considers:
- **Query intent** - What is the user trying to understand?
- **Data structure** - What fields are available?
- **Best practices** - Which chart type communicates best?
- **Context** - Previous queries and conversation flow

The agent can also create multiple visualizations when appropriate!
