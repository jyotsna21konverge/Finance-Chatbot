# Visualization Enhancement - Agent-Driven Chart Selection

## Overview
This enhancement enables the AR Agent to intelligently decide which type of visualization is most suitable for the data being presented, rather than relying on hardcoded pattern matching.

## Changes Made

### 1. New Visualization Tool (`tools/tools.py`)
Added `create_visualization` tool that allows the agent to specify:
- **chart_type**: bar, line, pie, table, metrics, or scatter
- **title**: Descriptive title for the visualization
- **data_source**: Which tool's data to visualize
- **x_field**: Field for x-axis (optional)
- **y_field**: Field for y-axis (optional)
- **description**: What the visualization shows

### 2. Enhanced System Prompt (`prompts.py`)
Updated the agent's system prompt to include:
- Responsibility for recommending appropriate visualizations
- Guidelines for when to use each chart type:
  - **Bar charts**: Comparisons (aging buckets, status counts)
  - **Line charts**: Trends over time (payment history)
  - **Pie charts**: Proportions (status distribution)
  - **Tables**: Detailed records (invoice lists)
  - **Metrics**: Key numbers (totals, averages)
  - **Scatter plots**: Correlations (credit vs overdue)

### 3. Updated Agent Configuration (`agents/agent.py`)
- Added `create_visualization` tool to the agent's toolset
- Tool is now available for the agent to call during query processing

### 4. Enhanced Streamlit UI (`streamlit_app.py`)

#### Modified `extract_tool_outputs()`:
- Now returns both tool outputs AND visualization configs
- Separates visualization recommendations from data

#### New `render_dynamic_visualization()`:
- Renders charts based on agent's recommendations
- Supports all chart types: bar, line, pie, table, metrics, scatter
- Handles data extraction and formatting automatically
- Provides fallback to table view if visualization fails

#### Updated `render_tool_data_visualization()`:
- First renders agent-recommended visualizations
- Then falls back to legacy pattern-matching for backward compatibility
- Shows count of agent-recommended charts

## How It Works

### Agent Workflow:
1. User asks a question (e.g., "Show me AR aging breakdown")
2. Agent retrieves data using appropriate tools (e.g., `get_ar_aging_report`)
3. Agent analyzes the data structure and query intent
4. Agent calls `create_visualization` to recommend chart type
5. UI receives both data and visualization config
6. UI renders the recommended visualization

### Example Agent Behavior:
```
User: "What's the status breakdown of all invoices?"

Agent thinks:
- Calls search_invoices() to get invoice data
- Sees data has "status" field with categories
- Decides bar chart is best for category comparison
- Calls create_visualization(
    chart_type="bar",
    title="Invoice Status Breakdown",
    data_source="search_invoices",
    x_field="status",
    y_field="count"
  )
```

## Benefits

1. **Intelligent Selection**: Agent chooses visualization based on:
   - Data structure and fields available
   - Query intent and context
   - Best practices for data visualization

2. **Flexibility**: Agent can:
   - Create multiple visualizations for complex queries
   - Choose different chart types for different data aspects
   - Adapt to new data patterns without code changes

3. **User Experience**: 
   - More relevant visualizations
   - Better data insights
   - Consistent with user's question intent

4. **Maintainability**:
   - Less hardcoded logic
   - Easier to add new chart types
   - Agent learns from prompt improvements

## Backward Compatibility

The system maintains backward compatibility:
- Legacy pattern-matching visualization still works
- If agent doesn't call `create_visualization`, default behavior applies
- Existing queries continue to work as before

## Testing Recommendations

Test with queries like:
- "Show me AR aging breakdown" → Should recommend bar chart
- "What's the trend of payments over time?" → Should recommend line chart
- "Show invoice status distribution" → Should recommend pie/bar chart
- "List all overdue invoices" → Should recommend table
- "What are the key AR metrics?" → Should recommend metrics display

## Future Enhancements

Potential improvements:
1. Add more chart types (heatmap, area, stacked bar)
2. Support multiple visualizations per query
3. Add chart customization (colors, labels, sorting)
4. Enable interactive filtering and drill-down
5. Export visualizations as images
6. Add visualization templates for common queries
