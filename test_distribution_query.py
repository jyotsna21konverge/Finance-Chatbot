"""
Test script to verify the agent can handle invoice distribution queries.
"""

from agents.agent import ask_agent
import json

def test_distribution_query():
    """Test the query: Show the distribution of total invoice amount for all the vendors."""
    
    print("=" * 80)
    print("Testing Query: Show the distribution of total invoice amount for all the vendors")
    print("=" * 80)
    
    query = "Show the distribution of total invoice amount for all the vendors."
    
    try:
        result = ask_agent(query)
        
        print("\n📊 FLOW RESULTS:")
        print("-" * 80)
        
        for step in result:
            step_type = step.get("type")
            
            if step_type == "user":
                print(f"\n👤 USER: {step.get('text')}")
            
            elif step_type == "assistant":
                print(f"\n🤖 ASSISTANT: {step.get('text')}")
                if step.get("tool_calls"):
                    print(f"   📞 Tool Calls: {len(step.get('tool_calls'))}")
                    for tc in step.get("tool_calls"):
                        print(f"      - {tc.get('name')}: {tc.get('args')}")
            
            elif step_type == "tool":
                tool_name = step.get("tool_name")
                output = step.get("output")
                print(f"\n🔧 TOOL: {tool_name}")
                
                # Show summary of output
                if isinstance(output, dict):
                    if output.get("ok"):
                        data = output.get("data", [])
                        if isinstance(data, list):
                            print(f"   ✓ Success: {len(data)} items returned")
                            if data and len(data) > 0:
                                print(f"   Sample: {json.dumps(data[0], indent=6)[:200]}...")
                        else:
                            print(f"   ✓ Success: {type(data).__name__} returned")
                    else:
                        print(f"   ✗ Error: {output.get('error')}")
                else:
                    print(f"   Output: {str(output)[:200]}...")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED")
        print("=" * 80)
        
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
        else:
            print("\n⚠️ WARNING: No final answer found in the flow!")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_distribution_query()
