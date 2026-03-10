"""
Test script to verify the agent creates pie chart for percentage queries.
"""

from agents.agent import ask_agent
import json

def test_percentage_query():
    """Test the query: What percentage of invoices are overdue?"""
    
    print("=" * 80)
    print("Testing Query: What percentage of invoices are overdue?")
    print("=" * 80)
    
    query = "What percentage of invoices are overdue?"
    
    try:
        result = ask_agent(query)
        
        print("\n📊 CHECKING FOR VISUALIZATION:")
        print("-" * 80)
        
        found_status_summary = False
        found_visualization = False
        
        for step in result:
            step_type = step.get("type")
            
            if step_type == "tool":
                tool_name = step.get("tool_name")
                output = step.get("output")
                
                if tool_name == "get_invoice_status_summary":
                    found_status_summary = True
                    print(f"\n✅ Found get_invoice_status_summary call")
                    if isinstance(output, dict) and output.get("ok"):
                        data = output.get("data", [])
                        print(f"   Data returned: {len(data)} status categories")
                        for item in data:
                            print(f"   - {item.get('status')}: {item.get('count')} invoices ({item.get('percentage')}%)")
                
                elif tool_name == "create_visualization":
                    found_visualization = True
                    print(f"\n✅ Found create_visualization call")
                    if isinstance(output, dict) and "visualization" in output:
                        viz = output["visualization"]
                        print(f"   Chart Type: {viz.get('chart_type')}")
                        print(f"   Title: {viz.get('title')}")
                        print(f"   Data Source: {viz.get('data_source')}")
                        print(f"   X Field: {viz.get('x_field')}")
                        print(f"   Y Field: {viz.get('y_field')}")
        
        print("\n" + "=" * 80)
        print("RESULTS:")
        print("=" * 80)
        
        if found_status_summary:
            print("✅ Agent called get_invoice_status_summary")
        else:
            print("❌ Agent did NOT call get_invoice_status_summary")
        
        if found_visualization:
            print("✅ Agent called create_visualization")
        else:
            print("❌ Agent did NOT call create_visualization")
            print("   This means no chart will be displayed!")
        
        # Extract final answer
        final_answer = None
        for step in reversed(result):
            if step.get("type") == "assistant":
                final_answer = step.get("text")
                break
        
        if final_answer:
            print("\n📝 FINAL ANSWER:")
            print("-" * 80)
            print(final_answer)
            print("-" * 80)
        
        if found_status_summary and found_visualization:
            print("\n🎉 SUCCESS! Agent should display a pie chart.")
        else:
            print("\n⚠️ WARNING: Agent may not display visualization properly.")
            print("   Check the system prompt and tool descriptions.")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_percentage_query()
