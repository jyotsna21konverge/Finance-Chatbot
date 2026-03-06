import streamlit as st
import requests
import json
import ast
from datetime import datetime
from agents.agent import ask_agent

def parse_output(output):
    """
    Safely parse tool output that might be JSON string or Python dict string.
    """
    if isinstance(output, dict):
        return output
    
    if isinstance(output, str):
        # Try JSON first
        try:
            return json.loads(output)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try Python literal eval
        try:
            parsed = ast.literal_eval(output)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            pass
        
        # If it's a simple string, return it as is
        return output
    
    # Fallback: return as is
    return output

# Page configuration
st.set_page_config(
    page_title="Payment Analytics Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    .chat-message {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        flex-direction: column;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4CAF50;
    }
    
    .final-answer {
        background-color: #c8e6c9;
        padding: 16px;
        border-radius: 8px;
        border-left: 5px solid #2e7d32;
        font-weight: 500;
        margin-bottom: 16px;
    }
    
    .step-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
        background-color: #fafafa;
    }
    
    .tool-step {
        background-color: #fff9c4;
        border-left: 3px solid #FBC02D;
    }
    
    .assistant-step {
        background-color: #e0f2f1;
        border-left: 3px solid #00897b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "current_session_idx" not in st.session_state:
    st.session_state.current_session_idx = None

# ============ SIDEBAR ============
with st.sidebar:
    # Logo
    st.image("assets/konvergeai_logo.png", use_container_width=True)
    
    st.markdown("---")
    
    # Chat History
    st.subheader("💬 Chat History")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_sessions.append({"messages": []})
        st.session_state.current_session_idx = len(st.session_state.chat_sessions) - 1
        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.chat_sessions:
        for idx, session in enumerate(st.session_state.chat_sessions):
            # Get first question as preview
            first_question = None
            for msg in session["messages"]:
                if msg["role"] == "user":
                    first_question = msg["content"]
                    break
            
            if first_question:
                preview = first_question[:40] + "..." if len(first_question) > 40 else first_question
            else:
                preview = "Empty Chat"
            
            # Highlight current session
            is_current = (st.session_state.current_session_idx == idx)
            button_label = f"📌 {preview}" if is_current else f"📝 {preview}"
            
            if st.button(button_label, key=f"session_{idx}", use_container_width=True):
                st.session_state.current_session_idx = idx
                st.rerun()
    else:
        st.info("No chat sessions yet. Start a conversation!")

# ============ MAIN CONTENT AREA ============
st.title("💰 Payment Analytics Agent")

# Create initial session if needed
if st.session_state.current_session_idx is None and len(st.session_state.chat_sessions) == 0:
    st.session_state.chat_sessions.append({"messages": []})
    st.session_state.current_session_idx = 0

# Display current session
if st.session_state.current_session_idx is not None and 0 <= st.session_state.current_session_idx < len(st.session_state.chat_sessions):
    current_session = st.session_state.chat_sessions[st.session_state.current_session_idx]
    
    if current_session["messages"]:
        # Display all messages in the current session
        for msg in current_session["messages"]:
            if msg["role"] == "user":
                st.markdown("### 📝 Your Question")
                st.markdown(f"**{msg['content']}**")
            
            elif msg["role"] == "assistant":
                st.markdown("### ✨ Final Answer")
                st.markdown(f"""
<div class="final-answer">
{msg['answer']}
</div>
""", unsafe_allow_html=True)
                
                if msg.get("steps"):
                    with st.expander("📋 View Processing Steps", expanded=False):
                        for i, step in enumerate(msg["steps"], 1):
                            if step["type"] == "user":
                                st.markdown(f"**Step {i} (User):** {step['text']}")
                            
                            elif step["type"] == "assistant":
                                st.markdown(f"**Step {i} (Assistant):** {step['text']}")
                                if step.get("tool_calls"):
                                    with st.expander(f"🔧 Tool Calls ({len(step['tool_calls'])})", expanded=False):
                                        for tool_call in step["tool_calls"]:
                                            st.code(json.dumps(tool_call, indent=2), language="json")
                            
                            elif step["type"] == "tool":
                                tool_name = step.get("tool_name", "Unknown")
                                st.markdown(f"**Step {i} (Tool: {tool_name})**")
                                with st.expander("Tool Output", expanded=False):
                                    tool_output = step.get("output", {})
                                    
                                    # Convert output to displayable format
                                    if isinstance(tool_output, str):
                                        # If it's a string, try to parse and display as formatted code
                                        try:
                                            parsed = ast.literal_eval(tool_output)
                                            st.code(json.dumps(parsed, indent=2, default=str), language="json")
                                        except:
                                            st.code(tool_output)
                                    elif isinstance(tool_output, dict):
                                        # If it's already a dict, format and display
                                        st.code(json.dumps(tool_output, indent=2, default=str), language="json")
                                    elif isinstance(tool_output, (list, tuple)):
                                        # If it's a list/tuple, format and display
                                        st.write("**Output List:**")
                                        for idx, item in enumerate(tool_output, 1):
                                            st.write(f"{idx}. {item}")
                                    else:
                                        # Fallback: display as text
                                        st.write(str(tool_output))
                
                st.markdown("---")
    else:
        st.info("Start a conversation by asking a question below!")

# ============ INPUT AREA ============
st.markdown("---")
st.subheader("Ask a Question")

col1, col2 = st.columns([5, 1])

with col1:
    user_question = st.text_input(
        "Enter your question:",
        placeholder="e.g., What are the customer summary for customer ID 1?",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤 Send", use_container_width=True)

# Process the question
if send_button and user_question.strip():
    with st.spinner("Processing your question..."):
        try:
            # Call the agent
            flow = ask_agent(user_question)
            
            # Extract final answer from the flow
            final_answer = ""
            for message in reversed(flow):
                if message["type"] == "assistant":
                    final_answer = message.get("text", "No answer generated")
                    break
            
            # Add to current session
            if st.session_state.current_session_idx is not None:
                current_session = st.session_state.chat_sessions[st.session_state.current_session_idx]
                
                # Add user message
                current_session["messages"].append({
                    "role": "user",
                    "content": user_question,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
                # Add assistant message with answer and steps
                current_session["messages"].append({
                    "role": "assistant",
                    "answer": final_answer,
                    "steps": flow,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            
            st.success("✅ Question processed successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.markdown("Please check your question and try again.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
    Finance Chatbot © 2025 | Powered by LangChain & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
