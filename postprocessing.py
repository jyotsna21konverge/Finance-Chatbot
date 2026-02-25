import json
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def extract_flow(result: dict):
    flow = []
    for i, m in enumerate(result["messages"]):
        if isinstance(m, HumanMessage):
            flow.append({
                "step": i,
                "type": "user",
                "text": m.content,
            })

        elif isinstance(m, AIMessage):
            flow.append({
                "step": i,
                "type": "assistant",
                "text": m.content,
                "tool_calls": m.tool_calls or [],
            })

        elif isinstance(m, ToolMessage):
            # ToolMessage.content is usually JSON text
            try:
                payload = json.loads(m.content)
            except Exception:
                payload = m.content

            flow.append({
                "step": i,
                "type": "tool",
                "tool_name": m.name,
                "tool_call_id": m.tool_call_id,
                "output": payload,
            })

        else:
            flow.append({"step": i, "type": type(m).__name__, "raw": str(m)})

    return flow