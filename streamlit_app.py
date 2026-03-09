import streamlit as st
import requests
import json
import ast
from datetime import datetime
from agents.agent import ask_agent
from dataconnectors.json_loader import json_loader
import pandas as pd

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

def get_ar_metrics():
    """Calculate AR metrics for dashboard."""
    try:
        balances = json_loader.get_balances()
        transactions = json_loader.get_transactions()
        credits = json_loader.get_credit_limits()
        
        total_ar = sum(b.get("ar_balance", 0) for b in balances)
        total_current = sum(b.get("current_due", 0) for b in balances)
        total_overdue = sum(b.get("overdue_30", 0) + b.get("overdue_60", 0) + b.get("overdue_90", 0) for b in balances)
        
        total_credit = sum(c.get("credit_limit", 0) for c in credits)
        total_used = sum(c.get("current_ar_balance", 0) for c in credits)
        total_available = total_credit - total_used
        
        num_vendors = len(balances)
        num_invoices = len(transactions)
        num_overdue_invoices = len([t for t in transactions if t.get("status") == "overdue"])
        
        pct_overdue = (total_overdue / total_ar * 100) if total_ar > 0 else 0
        pct_utilization = (total_used / total_credit * 100) if total_credit > 0 else 0
        
        return {
            "total_ar": total_ar,
            "current_due": total_current,
            "total_overdue": total_overdue,
            "pct_overdue": pct_overdue,
            "num_vendors": num_vendors,
            "num_invoices": num_invoices,
            "num_overdue_invoices": num_overdue_invoices,
            "total_credit": total_credit,
            "total_used": total_used,
            "total_available": total_available,
            "pct_utilization": pct_utilization,
        }
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")
        return {}

def render_dashboard():
    """Render AR summary dashboard."""
    st.markdown("### 📊 Accounts Receivable Summary Dashboard")
    st.markdown("---")
    
    try:
        metrics = get_ar_metrics()
        
        if not metrics:
            st.warning("Unable to load dashboard metrics")
            return
        
        # Key Metrics Row 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total AR Balance",
                f"${metrics['total_ar']:,.2f}",
                delta=f"{metrics['pct_overdue']:.1f}% overdue"
            )
        
        with col2:
            st.metric(
                "Current Due",
                f"${metrics['current_due']:,.2f}",
                delta=f"{metrics['num_vendors']} vendors"
            )
        
        with col3:
            st.metric(
                "Overdue Amount",
                f"${metrics['total_overdue']:,.2f}",
                delta=f"{metrics['num_overdue_invoices']} invoices"
            )
        
        with col4:
            st.metric(
                "Outstanding Invoices",
                f"{metrics['num_invoices']}",
                delta="Count"
            )
        
        st.markdown("---")
        
        # AR Breakdown Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 AR Aging Analysis")
            balances = json_loader.get_balances()
            
            current_total = sum(b.get("current_due", 0) for b in balances)
            overdue_30 = sum(b.get("overdue_30", 0) for b in balances)
            overdue_60 = sum(b.get("overdue_60", 0) for b in balances)
            overdue_90 = sum(b.get("overdue_90", 0) for b in balances)
            
            aging_data = {
                "Status": ["Current", "30+ Days", "60+ Days", "90+ Days"],
                "Amount": [current_total, overdue_30, overdue_60, overdue_90]
            }
            aging_df = pd.DataFrame(aging_data)
            
            st.bar_chart(aging_df.set_index("Status"))
            
            # Summary table
            st.markdown("**Aging Summary:**")
            summary_data = {
                "Bucket": ["Current", "30-60 Days", "60-90 Days", "90+ Days"],
                "Amount": [f"${current_total:,.2f}", f"${overdue_30:,.2f}", f"${overdue_60:,.2f}", f"${overdue_90:,.2f}"],
                "Percentage": [
                    f"{(current_total/metrics['total_ar']*100):.1f}%" if metrics['total_ar'] > 0 else "0%",
                    f"{(overdue_30/metrics['total_ar']*100):.1f}%" if metrics['total_ar'] > 0 else "0%",
                    f"{(overdue_60/metrics['total_ar']*100):.1f}%" if metrics['total_ar'] > 0 else "0%",
                    f"{(overdue_90/metrics['total_ar']*100):.1f}%" if metrics['total_ar'] > 0 else "0%",
                ]
            }
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        
        with col2:
            st.subheader("💳 Credit Utilization")
            
            credits = json_loader.get_credit_limits()
            credit_data = {
                "Vendor": [c.get("vendor_name", c.get("vendor_id", "Unknown"))[:20] for c in credits],
                "Limit": [c.get("credit_limit", 0) for c in credits],
                "Used": [c.get("current_ar_balance", 0) for c in credits],
                "Utilization %": [c.get("utilization_percent", 0) for c in credits]
            }
            credit_df = pd.DataFrame(credit_data)
            
            # Visualization
            fig_data = {
                "Status": ["Available Credit", "Used Credit"],
                "Amount": [metrics['total_available'], metrics['total_used']]
            }
            st.bar_chart(pd.DataFrame(fig_data).set_index("Status"))
            
            st.markdown("**Credit Utilization by Vendor:**")
            st.dataframe(credit_df[["Vendor", "Limit", "Used", "Utilization %"]], use_container_width=True)
        
        st.markdown("---")
        
        # At-Risk Vendors and Top Overdue
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚠️ At-Risk Vendors")
            
            # Get vendors with high overdue or utilization
            at_risk = []
            for balance in balances:
                overdue = balance.get("overdue_60", 0) + balance.get("overdue_90", 0)
                if overdue > 0:
                    vendor = next((p for p in json_loader.get_profiles() if p.get("vendor_id") == balance.get("vendor_id")), {})
                    at_risk.append({
                        "Vendor": vendor.get("vendor_name", balance.get("vendor_id")),
                        "Status": vendor.get("status", "Unknown"),
                        "Overdue 60+": f"${overdue:,.2f}",
                        "Credit Rating": vendor.get("credit_rating", "N/A")
                    })
            
            if at_risk:
                at_risk_df = pd.DataFrame(at_risk)
                st.dataframe(at_risk_df, use_container_width=True)
            else:
                st.info("No at-risk vendors detected")
        
        with col2:
            st.subheader("📋 Top Overdue Invoices")
            
            # Get top overdue invoices
            transactions = json_loader.get_transactions()
            overdue_invoices = [t for t in transactions if t.get("status") == "overdue"]
            overdue_invoices.sort(key=lambda x: x.get("amount_due", 0), reverse=True)
            
            top_overdue = []
            for invoice in overdue_invoices[:5]:
                vendor = next((p for p in json_loader.get_profiles() if p.get("vendor_id") == invoice.get("vendor_id")), {})
                top_overdue.append({
                    "Invoice": invoice.get("invoice_id"),
                    "Vendor": vendor.get("vendor_name", invoice.get("vendor_id")),
                    "Amount": f"${invoice.get("amount_due", 0):,.2f}",
                    "Status": invoice.get("payment_status", "Unknown")
                })
            
            if top_overdue:
                top_df = pd.DataFrame(top_overdue)
                st.dataframe(top_df, use_container_width=True)
            else:
                st.info("No overdue invoices")
        
        st.markdown("---")
        
        # Disputes and Issues
        st.subheader("🔴 Disputes & Critical Issues")
        
        disputes = json_loader.get_fraud_alerts()
        if disputes:
            dispute_data = []
            for dispute in disputes:
                dispute_data.append({
                    "Dispute ID": dispute.get("dispute_id"),
                    "Vendor": dispute.get("vendor_name", dispute.get("vendor_id")),
                    "Amount": f"${dispute.get('disputed_amount', 0):,.2f}",
                    "Reason": dispute.get("dispute_reason", "Unknown"),
                    "Status": dispute.get("dispute_status", "Unknown")
                })
            
            dispute_df = pd.DataFrame(dispute_data)
            st.dataframe(dispute_df, use_container_width=True)
        else:
            st.info("No disputes on record")
        
    except Exception as e:
        st.error(f"Error rendering dashboard: {str(e)}")
        st.markdown("Please try refreshing the page.")


# Page configuration
st.set_page_config(
    page_title="Accounts Receivable Agent",
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

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "dashboard"  # "dashboard" or "chat"

# ============ SIDEBAR ============
with st.sidebar:
    # Logo
    st.image("assets/konvergeai_logo.png", use_container_width=True)
    
    st.markdown("---")
    
    # View Toggle
    st.subheader("🎛️ Navigation")
    view_tabs = st.radio(
        "Select View:",
        ["📊 Dashboard", "💬 Chat"],
        key="view_selection",
        index=0 if st.session_state.view_mode == "dashboard" else 1
    )
    
    if "Dashboard" in view_tabs:
        st.session_state.view_mode = "dashboard"
    else:
        st.session_state.view_mode = "chat"
    
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
st.title("💰 Accounts Receivable Agent")

if st.session_state.view_mode == "dashboard":
    # ===== DASHBOARD VIEW =====
    render_dashboard()

else:
    # ===== CHAT VIEW =====
    st.markdown("""
---
### Welcome to the AR Management System
This intelligent agent helps you manage vendor relationships, track invoice payments, analyze aging reports, and resolve disputes.
Ask questions about vendor profiles, invoice status, AR balances, payment disputes, and more.
""")

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
        placeholder="e.g., What is the AR status for TechSupply Solutions? or Show all overdue invoices.",
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
    Accounts Receivable Agent © 2025 | Powered by LangChain & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
