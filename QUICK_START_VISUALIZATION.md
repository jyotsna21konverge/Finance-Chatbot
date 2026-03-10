# Quick Start: Agent-Driven Visualization

## What Changed?

The AR Agent can now intelligently decide which chart type to use for visualizing data, instead of relying on hardcoded rules.

## Recent Updates

### New Tool: `get_vendor_invoice_totals`
Added to handle queries about invoice distribution across vendors. This tool:
- Aggregates invoice amounts by vendor
- Calculates total, count, and average per vendor
- Enables queries like "Show the distribution of total invoice amount for all vendors"

## Key Changes

### 1. New Tool: `create_visualization`
Location: `tools/tools.py`

The agent can now call this tool to specify:
- Chart type (bar, line, pie, table, metrics, scatter)
- Title and description
- Which data to visualize
- Which fields to use for axes

### 2. New Tool: `get_vendor_invoice_totals`
Location: `tools/tools.py`

Aggregates invoice data by vendor:
- Total invoice amount per vendor
- Invoice count per vendor
- Average invoice amount per vendor
- Sorted by total amount (highest first)

### 3. Enhanced Agent Prompt
Location: `prompts.py`

The agent now knows:
- When to use each chart type
- How to analyze data for visualization
- Best practices for data presentation
- To use `get_vendor_invoice_totals` for distribution queries

### 4. Dynamic Rendering
Location: `streamlit_app.py`

The UI now:
- Extracts visualization recommendations from agent
- Renders charts based on agent's decisions
- Falls back to legacy behavior if needed

## How to Use

### For Users:
Just ask questions naturally! The agent will choose the best visualization:

```
"Show me AR aging breakdown" → Bar chart
"List overdue invoices" → Table
"What are key AR metrics?" → Metrics display
"Show payment trends" → Line chart
"Show the distribution of total invoice amount for all vendors" → Bar chart with vendor totals
```

### For Developers:
No code changes needed! The agent handles visualization decisions automatically.

To customize:
1. Update system prompt in `prompts.py` to adjust guidelines
2. Add new chart types in `render_dynamic_visualization()` in `streamlit_app.py`
3. Modify `create_visualization` tool for new parameters

## Testing

Run the Streamlit app and try these queries:

1. **"What's the AR aging breakdown?"**
   - Expected: Bar chart with aging buckets

2. **"Show all invoices for vendor V001"**
   - Expected: Table with invoice details

3. **"What are the total AR and overdue amounts?"**
   - Expected: Metrics display

4. **"Give me a complete AR overview"**
   - Expected: Multiple visualizations (metrics + charts + tables)

5. **"Show the distribution of total invoice amount for all the vendors"**
   - Expected: Bar chart showing total invoice amounts by vendor

### Test Script
Run the test script to verify the distribution query:
```bash
python test_distribution_query.py
```

## Benefits

✅ **Intelligent**: Agent chooses based on data and context
✅ **Flexible**: Can create multiple visualizations per query
✅ **Maintainable**: Less hardcoded logic
✅ **User-friendly**: More relevant visualizations
✅ **Extensible**: Easy to add new chart types
✅ **Aggregation**: Handles complex data grouping and calculations

## Files Modified

1. `tools/tools.py` - Added `create_visualization` and `get_vendor_invoice_totals` tools
2. `prompts.py` - Enhanced system prompt with visualization guidelines
3. `agents/agent.py` - Added visualization and aggregation tools to agent
4. `streamlit_app.py` - Updated rendering logic for dynamic visualizations

## Backward Compatibility

✅ Existing queries still work
✅ Legacy pattern-matching preserved as fallback
✅ No breaking changes

## Troubleshooting

### Issue: Agent not showing answer
**Possible causes:**
1. Agent might not be generating a final response text
2. Tool might be returning an error
3. Visualization config might be malformed

**Solutions:**
1. Check the flow/steps in the Streamlit UI expander
2. Run the test script to see detailed output
3. Verify the tool is being called correctly
4. Check that the agent's final message contains text

### Issue: Visualization not rendering
**Possible causes:**
1. Data fields don't match visualization config
2. Data format is incompatible
3. Chart type not supported

**Solutions:**
1. Check that x_field and y_field exist in the data
2. Verify data is in list of dicts format
3. Review `render_dynamic_visualization()` for supported types

## Next Steps

1. Test with various queries
2. Monitor agent's visualization choices
3. Refine prompt guidelines based on results
4. Add more chart types as needed
5. Consider adding chart customization options
6. Add more aggregation tools for complex queries
