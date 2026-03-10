"""
Test script to verify time-based query functionality.
"""

from agents.agent import ask_agent
import json

def test_time_based_query():
    """Test the query: List all vendors which raised invoices in last 1 month and their outstanding amounts"""
    
    print("=" * 80)
    print("Testing Query: List all vendors which raised invoices in last 1 month")
    print("and their total outstanding amount for the same time")
    print("=" * 80)
    
    query = "List all vendors which raised invoices in last 1 month and their total outstanding amount for the same time"
    
    try:
        result = ask_agent(query)
        
        print("\n📊 CHECKING FOR TIME-BASED ANALYSIS:")
        print("-" * 80)
        
        found_time_tool = False
        found_visualization = False
        
        for step in result:
            step_type = step.get("type")
            
            if step_type == "tool":
                tool_name = step.get("tool_name")
                output = step.get("output")
                
                if tool_name == "get_vendor_outstanding_by_period":
                    found_time_tool = True
                    print(f"\n✅ Found get_vendor_outstanding_by_period call")
                    if isinstance(output, dict) and output.get("ok"):
                        data = output.get("data", [])
                        print(f"   Vendors found: {len(data)}")
                        print(f"   Days back: {output.get('days_back')}")
                        for vendor in data[:3]:  # Show first 3
                            print(f"   - {vendor.get('vendor_name')}: {vendor.get('invoice_count')} invoices, "
                                  f"${vendor.get('total_outstanding_amount')} outstanding")
                
                elif tool_name == "create_visualization":
                    found_visualization = True
                    print(f"\n✅ Found create_visualization call")
                    if isinstance(output, dict) and "visualization" in output:
                        viz = output["visualization"]
                        print(f"   Chart Type: {viz.get('chart_type')}")
                        print(f"   Title: {viz.get('title')}")
                        print(f"   Data Source: {viz.get('data_source')}")
        
        print("\n" + "=" * 80)
        print("RESULTS:")
        print("=" * 80)
        
        if found_time_tool:
            print("✅ Agent called get_vendor_outstanding_by_period")
        else:
            print("❌ Agent did NOT call get_vendor_outstanding_by_period")
        
        if found_visualization:
            print("✅ Agent called create_visualization")
        else:
            print("❌ Agent did NOT call create_visualization")
        
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
        
        if found_time_tool and found_visualization:
            print("\n🎉 SUCCESS! Agent can answer time-based queries.")
        else:
            print("\n⚠️ WARNING: Agent may not be using time-based tools properly.")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_date_range_query():
    """Test with specific date range"""
    
    print("\n\n" + "=" * 80)
    print("Testing Query: Show invoices between Feb 1 and Mar 10, 2026")
    print("=" * 80)
    
    query = "Show me invoices between February 1 and March 10, 2026 and their outstanding amounts"
    
    try:
        result = ask_agent(query)
        
        print("\n📊 CHECKING FOR DATE RANGE ANALYSIS:")
        print("-" * 80)
        
        for step in result:
            if step.get("type") == "tool":
                tool_name = step.get("tool_name")
                if tool_name == "get_invoices_by_date_range":
                    print(f"✅ Found get_invoices_by_date_range call")
                    output = step.get("output")
                    if isinstance(output, dict) and output.get("ok"):
                        print(f"   Invoices found: {output.get('count')}")
                        print(f"   Date range: {output.get('start_date')} to {output.get('end_date')}")
        
        # Extract final answer
        final_answer = None
        for step in reversed(result):
            if step.get("type") == "assistant":
                final_answer = step.get("text")
                break
        
        if final_answer:
            print("\n📝 FINAL ANSWER:")
            print("-" * 80)
            print(final_answer[:500])  # First 500 chars
            print("-" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_time_based_query()
    test_date_range_query()
