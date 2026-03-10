# Pie Chart Fix - "What percentage of invoices are overdue?"

## Problem Identified

When user asked "What percentage of invoices are overdue?", the agent:
- ✅ Provided a good text answer (30.3% overdue)
- ✅ Called `get_ar_summary` to get data
- ❌ Did NOT call `create_visualization` to generate a pie chart
- ❌ No chart was displayed

**Root Cause:** The `get_ar_summary` tool returns complex nested data that's not suitable for direct visualization. The agent needs a tool that returns invoice status data in a format ready for pie charts.

## Solution Implemented

### 1. Created New Tool: `get_invoice_status_summary`
**File:** `tools/tools.py`

This tool specifically handles invoice status analysis:
- Gets all invoices
- Groups by status (current, overdue, paid)
- Calculates counts and totals per status
- Calculates percentages automatically
- Returns data in perfect format for pie charts

**Output Format:**
```python
{
    "ok": True,
    "total_invoices": 66,
    "data": [
        {
            "status": "Current",
            "count": 30,
            "total_amount": 500000.00,
            "percentage": 45.5
        },
        {
            "status": "Overdue",
            "count": 20,
            "total_amount": 350000.00,
            "percentage": 30.3
        },
        {
            "status": "Paid",
            "count": 16,
            "total_amount": 250000.00,
            "percentage": 24.2
        }
    ]
}
```

### 2. Added Tool to Agent
**File:** `agents/agent.py`
- Imported `get_invoice_status_summary`
- Added to agent's tool list

### 3. Enhanced System Prompt
**File:** `prompts.py`

Added specific instructions:
- Guideline 9: "For queries about invoice status percentages or distribution, use get_invoice_status_summary tool"
- Guideline 11: "CRITICAL: After retrieving data, you MUST call create_visualization to show the data visually"
- Emphasized that percentage queries MUST result in pie charts

### 4. Created Test Script
**File:** `test_percentage_query.py`
- Tests the specific query
- Checks if both tools are called
- Validates visualization config
- Shows detailed output

## How It Works Now

### Query: "What percentage of invoices are overdue?"

**Expected Flow:**
1. Agent calls `get_invoice_status_summary()`
2. Tool returns status breakdown with percentages
3. Agent calls `create_visualization()`:
   ```python
   create_visualization(
       chart_type="pie",
       title="Invoice Status Distribution",
       data_source="get_invoice_status_summary",
       x_field="status",
       y_field="count",  # or "percentage"
       description="Percentage breakdown of invoices by status"
   )
   ```
4. Agent provides text answer: "Approximately 30.3% of invoices are overdue..."
5. UI renders interactive pie chart showing all statuses

**Result:**
- Text answer with exact percentage
- Interactive donut chart with slices for each status
- Data table showing exact counts and amounts
- Visual representation of the distribution

## Testing

Run the test script:
```bash
python test_percentage_query.py
```

Expected output:
```
✅ Agent called get_invoice_status_summary
✅ Agent called create_visualization
   Chart Type: pie
   Title: Invoice Status Distribution
   Data Source: get_invoice_status_summary
   X Field: status
   Y Field: count

🎉 SUCCESS! Agent should display a pie chart.
```

## Why This Fix Works

### Before:
- `get_ar_summary` returns nested complex data
- Not suitable for direct visualization
- Agent couldn't easily create chart from it
- No clear guidance on which tool to use

### After:
- `get_invoice_status_summary` returns flat, chart-ready data
- Includes pre-calculated percentages
- Clear tool description for status queries
- Explicit prompt instructions to create visualizations
- Perfect format for pie charts

## Similar Queries That Now Work

All these should now generate pie charts:

1. "What percentage of invoices are overdue?"
2. "Show the distribution of invoice statuses"
3. "What's the breakdown of invoices by status?"
4. "How many invoices are current vs overdue?"
5. "Show invoice status composition"

## Files Modified

1. `tools/tools.py` - Added `get_invoice_status_summary` tool
2. `agents/agent.py` - Added tool to agent
3. `prompts.py` - Enhanced with specific instructions
4. `test_percentage_query.py` - Created test script

## Next Steps

1. **Test the query again** in Streamlit
2. **Run test script** to verify tool calls
3. **Check "View Processing Steps"** to see tool execution
4. **Verify pie chart appears** with correct data

If the chart still doesn't appear:
- Check that agent called both tools
- Verify visualization config has correct fields
- Ensure plotly is installed: `pip install plotly`
- Check for errors in browser console

## Key Takeaway

For the agent to create visualizations automatically, you need:
1. ✅ Tool that returns visualization-ready data
2. ✅ Clear tool description matching query intent
3. ✅ Explicit prompt instructions to create visualizations
4. ✅ Data format that matches visualization requirements

The agent now has all of these for invoice status queries!
