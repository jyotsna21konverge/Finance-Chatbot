# Troubleshooting Agent Responses

## Issue: Agent Not Showing Answer

### Symptoms
- User submits a query
- Processing spinner completes
- No final answer appears in the UI
- Or answer appears but is empty/incomplete

### Common Causes & Solutions

#### 1. Agent Not Generating Final Response Text

**Diagnosis:**
- Check the "View Processing Steps" expander
- Look for the last assistant message
- Verify it contains actual text content

**Solution:**
Update the system prompt to emphasize providing clear answers:
```python
# In prompts.py
"9. Always provide a clear, natural language answer summarizing the data"
```

#### 2. Tool Returns Error Instead of Data

**Diagnosis:**
- Check tool outputs in the processing steps
- Look for `{"ok": False, "error": "..."}` responses

**Common Tool Errors:**
- Invalid parameters (e.g., vendor_id not found)
- Data format issues
- Missing required fields

**Solution:**
```python
# Verify tool is being called with correct parameters
# Check that data exists for the query
# Example: If querying vendor "V001", ensure it exists in data/profiles.json
```

#### 3. Visualization Config Malformed

**Diagnosis:**
- Check if `create_visualization` tool was called
- Verify the output has correct structure
- Look for missing required fields

**Solution:**
```python
# Correct visualization config structure:
{
    "ok": True,
    "visualization": {
        "chart_type": "bar",  # Required
        "title": "Chart Title",  # Required
        "data_source": "tool_name",  # Required
        "x_field": "field_name",  # Optional but recommended
        "y_field": "field_name",  # Optional but recommended
        "description": "What this shows"  # Optional
    }
}
```

#### 4. Data Format Incompatibility

**Diagnosis:**
- Tool returns data but visualization fails
- Check data structure in tool output
- Verify fields exist that visualization expects

**Solution:**
```python
# Ensure data is in correct format:
# - List of dictionaries for most charts
# - Each dict should have the fields specified in x_field/y_field
# Example:
[
    {"vendor_name": "Vendor A", "total_amount": 10000},
    {"vendor_name": "Vendor B", "total_amount": 15000}
]
```

### Debugging Steps

#### Step 1: Check the Flow
```python
# In streamlit_app.py, the flow is extracted from agent response
# Look at the "View Processing Steps" expander to see:
# 1. What tools were called
# 2. What parameters were used
# 3. What data was returned
# 4. What the agent's final message says
```

#### Step 2: Run Test Script
```bash
python test_distribution_query.py
```

This will show:
- Each step in the agent's reasoning
- Tool calls and their outputs
- Final answer extraction
- Any errors that occurred

#### Step 3: Check Tool Output Format
```python
# Tools should return:
{
    "ok": True,
    "data": [...]  # or {...}
}

# NOT just:
[...]  # Raw list

# The wrapper format helps with error handling
```

#### Step 4: Verify Agent Has Access to Tool
```python
# In agents/agent.py, ensure tool is imported and added:
from tools.tools import (
    create_visualization,
    get_vendor_invoice_totals,  # Make sure new tools are here
    # ... other tools
)

agent = create_agent(
    model=llm_pipe,
    tools=[
        create_visualization,
        get_vendor_invoice_totals,  # And here
        # ... other tools
    ],
    system_prompt=concierge_system_prompt,
)
```

### Specific Query Issues

#### Query: "Show the distribution of total invoice amount for all the vendors"

**What Should Happen:**
1. Agent calls `get_vendor_invoice_totals()`
2. Tool returns aggregated data by vendor
3. Agent calls `create_visualization()` with:
   - chart_type: "bar"
   - data_source: "get_vendor_invoice_totals"
   - x_field: "vendor_name"
   - y_field: "total_invoice_amount"
4. Agent provides text summary
5. UI renders bar chart

**If It Fails:**

Check 1: Does `get_vendor_invoice_totals` exist?
```bash
grep -n "get_vendor_invoice_totals" tools/tools.py
grep -n "get_vendor_invoice_totals" agents/agent.py
```

Check 2: Is the tool returning data?
```python
# Run in Python console:
from tools.tools import get_vendor_invoice_totals
result = get_vendor_invoice_totals()
print(result)
# Should show: {"ok": True, "count": X, "data": [...]}
```

Check 3: Is the agent calling it?
- Look in "View Processing Steps"
- Should see tool call with name "get_vendor_invoice_totals"

Check 4: Is visualization being created?
- Look for "create_visualization" tool call
- Check parameters match data structure

### Common Error Messages

#### "No tool data available to visualize"
**Cause:** No tools returned data, or data was filtered out
**Fix:** Check that tools are being called and returning non-empty data

#### "Required fields not found: X, Y"
**Cause:** Visualization config specifies fields that don't exist in data
**Fix:** Verify field names match exactly (case-sensitive)

#### "Data format not suitable for visualization"
**Cause:** Data is not a list of dicts
**Fix:** Check tool output format, ensure it returns proper structure

#### "Error rendering visualization: ..."
**Cause:** Exception during chart rendering
**Fix:** Check error details, verify data types (numbers vs strings)

### Prevention Best Practices

1. **Always Return Structured Data:**
```python
# Good:
return {"ok": True, "data": results}

# Bad:
return results
```

2. **Validate Tool Parameters:**
```python
if not vendor_id or not isinstance(vendor_id, str):
    return {"ok": False, "error": "vendor_id must be a non-empty string"}
```

3. **Provide Clear Error Messages:**
```python
return {"ok": False, "error": f"No data found for vendor_id: {vendor_id}"}
```

4. **Test Tools Independently:**
```python
# Create test scripts for each tool
from tools.tools import get_vendor_invoice_totals
result = get_vendor_invoice_totals(limit=5)
assert result["ok"] == True
assert len(result["data"]) > 0
```

5. **Update System Prompt:**
```python
# Make sure agent knows about new tools and when to use them
"8. For queries about invoice distribution or totals by vendor, use get_vendor_invoice_totals tool"
```

### Getting Help

If issues persist:

1. **Collect Information:**
   - Exact query that failed
   - Processing steps from UI
   - Error messages (if any)
   - Tool outputs

2. **Check Logs:**
   - Streamlit console output
   - Any Python exceptions
   - API errors (OpenAI)

3. **Simplify Query:**
   - Try simpler version of query
   - Test individual tools
   - Verify data exists

4. **Review Recent Changes:**
   - Check git diff
   - Verify all files saved
   - Restart Streamlit app

### Quick Fixes Checklist

- [ ] Restart Streamlit app
- [ ] Check .env file has valid API key
- [ ] Verify data files exist and are valid JSON
- [ ] Run test script to isolate issue
- [ ] Check tool is imported and added to agent
- [ ] Verify system prompt mentions the tool
- [ ] Check data format matches expected structure
- [ ] Look for typos in field names
- [ ] Ensure all required parameters provided
- [ ] Check for Python syntax errors
