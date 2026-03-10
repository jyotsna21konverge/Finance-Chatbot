import streamlit as st
import requests
import json
import ast
import re
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

def extract_tool_outputs(flow):
    """Extract all tool outputs from the flow/steps."""
    tool_outputs = {}
    
    if not flow:
        return tool_outputs
    
    for step in flow:
        if not isinstance(step, dict):
            continue
        
        if step.get("type") == "tool":
            tool_name = step.get("tool_name", "unknown")
            output = step.get("output", {})
            parsed_output = parse_output(output)
            
            # Skip if output is empty or None
            if not parsed_output:
                continue
            
            # Handle wrapped responses like {'ok': True, 'data': [...]}
            if isinstance(parsed_output, dict) and 'data' in parsed_output:
                parsed_output = parsed_output['data']
            
            if tool_name not in tool_outputs:
                tool_outputs[tool_name] = []
            
            if isinstance(parsed_output, list):
                # Filter out None/empty items
                valid_items = [item for item in parsed_output if item]
                tool_outputs[tool_name].extend(valid_items)
            elif isinstance(parsed_output, dict):
                tool_outputs[tool_name].append(parsed_output)
    
    return tool_outputs

def render_tool_data_visualization(tool_outputs):
    """Render visualizations based on tool output data."""
    st.markdown("### 📊 Data Visualization")
    
    if not tool_outputs:
        st.info("No tool data available to visualize")
        return
    
    for tool_name, data_list in tool_outputs.items():
        if not data_list or not any(data_list):
            continue
        
        try:
            # SPECIAL HANDLING: Vendor Summary returns a dict with nested fields
            if "summary" in tool_name.lower():
                with st.expander(f"👥 {tool_name}", expanded=True):
                    for item in data_list:
                        if not isinstance(item, dict):
                            continue
                        
                        # Extract nested summary fields
                        profile = item.get("profile", {})
                        ar_balance = item.get("ar_balance", [])
                        invoices = item.get("invoices", [])
                        credit_terms = item.get("credit_terms", [])
                        disputes = item.get("disputes", [])
                        
                        # Display profile
                        if profile and isinstance(profile, dict):
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Vendor Name", str(profile.get("vendor_name", "N/A"))[:20])
                            with col2:
                                st.metric("Credit Rating", profile.get("credit_rating", "N/A"))
                            with col3:
                                st.metric("Status", profile.get("status", "N/A"))
                            with col4:
                                st.metric("Payment Terms", profile.get("payment_terms", "N/A"))
                            
                            st.markdown("**Profile Details:**")
                            profile_df = pd.DataFrame([profile])
                            st.dataframe(profile_df, use_container_width=True)
                            st.divider()
                        
                        # Display AR Balance
                        if ar_balance and isinstance(ar_balance, list) and len(ar_balance) > 0:
                            st.subheader("AR Balance")
                            balance_item = ar_balance[0] if isinstance(ar_balance[0], dict) else {}
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Current", f"${float(balance_item.get('current_due', 0)):,.2f}")
                            with col2:
                                st.metric("30+ Days", f"${float(balance_item.get('overdue_30', 0)):,.2f}")
                            with col3:
                                st.metric("60+ Days", f"${float(balance_item.get('overdue_60', 0)):,.2f}")
                            with col4:
                                st.metric("90+ Days", f"${float(balance_item.get('overdue_90', 0)):,.2f}")
                            st.divider()
                        
                        # Display Credit Terms
                        if credit_terms and isinstance(credit_terms, list):
                            st.subheader("Credit Terms")
                            for ct in credit_terms:
                                if isinstance(ct, dict):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Credit Limit", f"${float(ct.get('credit_limit', 0)):,.2f}")
                                    with col2:
                                        st.metric("Used", f"${float(ct.get('current_ar_balance', 0)):,.2f}")
                                    with col3:
                                        st.metric("Utilization %", f"{ct.get('utilization_percent', 0):.1f}%")
                            st.divider()
                        
                        # Display Invoices
                        if invoices and isinstance(invoices, list):
                            st.subheader("Recent Invoices")
                            invoice_list = []
                            for inv in invoices:
                                if isinstance(inv, dict):
                                    invoice_list.append({
                                        "Invoice ID": inv.get("invoice_id", "N/A"),
                                        "Amount": f"${float(inv.get('invoice_amount', inv.get('amount', 0))):,.2f}",
                                        "Amount Due": f"${float(inv.get('amount_due', 0)):,.2f}",
                                        "Status": str(inv.get("status", "N/A")).upper(),
                                        "Due Date": inv.get("due_date", "N/A")
                                    })
                            if invoice_list:
                                df = pd.DataFrame(invoice_list)
                                st.dataframe(df, use_container_width=True)
                                st.divider()
                        
                        # Display Disputes
                        if disputes and isinstance(disputes, list) and len(disputes) > 0:
                            st.subheader("Disputes")
                            st.warning(f"⚠️ {len(disputes)} dispute(s) found")
                            dispute_list = []
                            for disp in disputes:
                                if isinstance(disp, dict):
                                    dispute_list.append({
                                        "Dispute ID": disp.get("dispute_id", "N/A"),
                                        "Amount": f"${float(disp.get('disputed_amount', 0)):,.2f}",
                                        "Status": disp.get("dispute_status", "N/A")
                                    })
                            if dispute_list:
                                df = pd.DataFrame(dispute_list)
                                st.dataframe(df, use_container_width=True)
                continue  # Skip other processing for summary
            
            # Ensure data_list is a list
            if not isinstance(data_list, list):
                data_list = [data_list]
            
            # Check for more specific patterns FIRST (invoice, credit, dispute, aging)
            # Then check general patterns (vendor)
            
            # Handle invoice data - CHECK FIRST (before vendor)
            if "invoice" in tool_name.lower():
                with st.expander(f"📋 {tool_name}", expanded=True):
                    invoice_list = []
                    for item in data_list:
                        if not isinstance(item, dict):
                            continue
                        # Handle both 'amount' and 'invoice_amount' field names
                        amount = float(item.get('invoice_amount', item.get('amount', 0)))
                        invoice_list.append({
                            "Invoice ID": item.get("invoice_id", "N/A"),
                            "Vendor": item.get("vendor_name", "N/A"),
                            "Amount": f"${amount:,.2f}",
                            "Due": f"${float(item.get('amount_due', 0)):,.2f}",
                            "Status": str(item.get("status", "N/A")).upper(),
                            "Due Date": item.get("due_date", "N/A")
                        })
                    
                    if invoice_list:
                        df = pd.DataFrame(invoice_list)
                        st.dataframe(df, use_container_width=True)
                        
                        # Status breakdown chart
                        status_counts = {}
                        for item in data_list:
                            if isinstance(item, dict):
                                status = str(item.get("status", "unknown")).upper()
                                status_counts[status] = status_counts.get(status, 0) + 1
                        
                        if status_counts:
                            chart_df = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
                            st.bar_chart(chart_df.set_index("Status"))
            
            # Handle credit/terms data - CHECK BEFORE VENDOR
            elif "credit" in tool_name.lower() or "payment_terms" in tool_name.lower() or "terms" in tool_name.lower():
                with st.expander(f"💳 {tool_name}", expanded=True):
                    credit_list = []
                    total_limit = 0
                    total_used = 0
                    
                    for item in data_list:
                        if not isinstance(item, dict):
                            continue
                        limit = float(item.get("credit_limit", 0) or 0)
                        used = float(item.get("current_ar_balance", 0) or 0)
                        total_limit += limit
                        total_used += used
                        
                        credit_list.append({
                            "Vendor": item.get("vendor_name", item.get("vendor_id", "N/A")),
                            "Limit": f"${limit:,.2f}",
                            "Used": f"${used:,.2f}",
                            "Utilization %": f"{item.get('utilization_percent', 0):.1f}%"
                        })
                    
                    if credit_list:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Credit Limit", f"${total_limit:,.2f}")
                        with col2:
                            st.metric("Total Used", f"${total_used:,.2f}")
                        with col3:
                            st.metric("Total Available", f"${total_limit - total_used:,.2f}")
                        
                        df = pd.DataFrame(credit_list)
                        st.dataframe(df, use_container_width=True)
                        
                        # Visualization
                        if total_limit > 0:
                            chart_data = {
                                "Status": ["Available Credit", "Used Credit"],
                                "Amount": [max(0, total_limit - total_used), total_used]
                            }
                            st.bar_chart(pd.DataFrame(chart_data).set_index("Status"))
            
            # Handle AR aging data - CHECK BEFORE VENDOR
            elif "aging" in tool_name.lower() or "balance" in tool_name.lower():
                with st.expander(f"📊 {tool_name}", expanded=True):
                    current_total = 0
                    overdue_30 = 0
                    overdue_60 = 0
                    overdue_90 = 0
                    
                    for item in data_list:
                        if isinstance(item, dict):
                            current_total += float(item.get("current_due", 0) or 0)
                            overdue_30 += float(item.get("overdue_30", 0) or 0)
                            overdue_60 += float(item.get("overdue_60", 0) or 0)
                            overdue_90 += float(item.get("overdue_90", 0) or 0)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current", f"${current_total:,.2f}")
                    with col2:
                        st.metric("30+ Days", f"${overdue_30:,.2f}")
                    with col3:
                        st.metric("60+ Days", f"${overdue_60:,.2f}")
                    with col4:
                        st.metric("90+ Days", f"${overdue_90:,.2f}")
                    
                    # Chart
                    aging_chart_data = {
                        "Status": ["Current", "30+ Days", "60+ Days", "90+ Days"],
                        "Amount": [current_total, overdue_30, overdue_60, overdue_90]
                    }
                    st.bar_chart(pd.DataFrame(aging_chart_data).set_index("Status"))
            
            # Handle disputes data - CHECK BEFORE VENDOR
            elif "dispute" in tool_name.lower():
                with st.expander(f"🔴 {tool_name}", expanded=True):
                    dispute_list = []
                    total_disputed = 0
                    
                    for item in data_list:
                        if isinstance(item, dict):
                            amount = float(item.get("disputed_amount", 0) or 0)
                            total_disputed += amount
                            
                            dispute_list.append({
                                "Dispute ID": item.get("dispute_id", "N/A"),
                                "Vendor": item.get("vendor_name", item.get("vendor_id", "N/A")),
                                "Amount": f"${amount:,.2f}",
                                "Reason": item.get("dispute_reason", "N/A"),
                                "Status": item.get("dispute_status", "N/A")
                            })
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Disputes", len(dispute_list))
                    with col2:
                        st.metric("Total Amount", f"${total_disputed:,.2f}")
                    
                    if dispute_list:
                        df = pd.DataFrame(dispute_list)
                        st.dataframe(df, use_container_width=True)
            
            # Handle vendor profile data - AFTER more specific checks
            elif "vendor" in tool_name.lower():
                with st.expander(f"👥 {tool_name}", expanded=True):
                    for item in data_list:
                        if not isinstance(item, dict):
                            continue
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Vendor Name", str(item.get("vendor_name", "N/A"))[:20])
                        with col2:
                            st.metric("Credit Rating", item.get("credit_rating", "N/A"))
                        with col3:
                            st.metric("Status", item.get("status", "N/A"))
                        with col4:
                            st.metric("Payment Terms", item.get("payment_terms", "N/A"))
                        
                        # Display as table
                        st.markdown("**Vendor Details:**")
                        df_data = pd.DataFrame([{k: v for k, v in item.items() if k not in ['id', 'vendor_id']}])
                        st.dataframe(df_data, use_container_width=True)
                        st.divider()
            
            # Generic data table for other tools
            else:
                with st.expander(f"📈 {tool_name}", expanded=True):
                    valid_items = [item for item in data_list if isinstance(item, dict)]
                    if valid_items:
                        df = pd.DataFrame(valid_items)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write("No structured data to display")
        
        except Exception as e:
            st.warning(f"Error rendering {tool_name} visualization: {str(e)}")

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
    /* Light Theme (Default) */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --text-primary: #000000;
        --text-secondary: #666666;
        --border-color: #e0e0e0;
        --success-bg: #c8e6c9;
        --info-bg: #bbdefb;
        --warning-bg: #fff9c4;
    }
    
    /* Dark Theme */
    [data-testid="stAppViewContainer"].dark-theme {
        --bg-primary: #1e1e1e;
        --bg-secondary: #2d2d2d;
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
        --border-color: #404040;
        --success-bg: #1b5e20;
        --info-bg: #0d47a1;
        --warning-bg: #f57f17;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
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
        background-color: var(--success-bg);
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
        background-color: var(--bg-secondary);
    }
    
    .tool-step {
        background-color: var(--warning-bg);
        border-left: 3px solid #FBC02D;
    }
    
    .assistant-step {
        background-color: #e0f2f1;
        border-left: 3px solid #00897b;
    }
    
    /* Theme Toggle Button Styling */
    .theme-toggle-btn {
        width: 100%;
        padding: 10px;
        border: 2px solid #ccc;
        border-radius: 8px;
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .theme-toggle-btn:hover {
        border-color: #2196F3;
        background-color: #e3f2fd;
    }
    
    /* Dark Theme Specific Overrides */
    body.dark-mode {{
        background-color: #1e1e1e;
        color: #ffffff;
    }}
    
    body.dark-mode [data-testid="stMainBlockContainer"] {{
        background-color: #1e1e1e;
    }}
    
    body.dark-mode .user-message {{
        background-color: #1d3a70;
        color: #ffffff;
    }}
    
    body.dark-mode .assistant-message {{
        background-color: #2d2d2d;
        color: #ffffff;
    }}
    
    body.dark-mode .final-answer {{
        background-color: #1b5e20;
        color: #ffffff;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state FIRST - before any session state access
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "current_session_idx" not in st.session_state:
    st.session_state.current_session_idx = None

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "dashboard"  # "dashboard" or "chat"

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "light"  # "light" or "dark"

# Apply theme-specific CSS AFTER session state initialization
if st.session_state.app_theme == "dark":
    st.markdown("""
    <style>
        /* Dark Mode Root */
        [data-testid="stAppViewContainer"] {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        
        [data-testid="stMainBlockContainer"] {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        /* Text and typography */
        body {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        
        p, span, div, h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        /* Labels and captions */
        label {
            color: #ffffff !important;
        }
        
        [data-testid="stCaption"] {
            color: #b0b0b0 !important;
        }
        
        /* Markdown text */
        [data-testid="stMarkdownContainer"] {
            color: #ffffff !important;
        }
        
        [data-testid="stMarkdownContainer"] p {
            color: #ffffff !important;
        }
        
        /* Chat and message boxes */
        .user-message {
            background-color: #1d3a70 !important;
            color: #ffffff !important;
            border-left: 4px solid #2196F3 !important;
        }
        
        .assistant-message {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
            border-left: 4px solid #4CAF50 !important;
        }
        
        .final-answer {
            background-color: #1b5e20 !important;
            color: #ffffff !important;
            border-left: 5px solid #66bb6a !important;
        }
        
        .step-item {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        .tool-step {
            background-color: #3d3d00 !important;
            color: #ffffff !important;
            border-left: 3px solid #FBC02D !important;
        }
        
        .assistant-step {
            background-color: #0d3d3d !important;
            color: #ffffff !important;
            border-left: 3px solid #00897b !important;
        }
        
        /* Metrics */
        [data-testid="stMetricContainer"] {
            background-color: #2d2d2d !important;
        }
        
        [data-testid="stMetricContainer"] p {
            color: #ffffff !important;
        }
        
        [data-testid="metric"] {
            color: #ffffff !important;
        }
        
        /* Dataframe and tables */
        [data-testid="stDataFrame"] {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        [data-testid="stDataFrame"] thead {
            background-color: #404040 !important;
        }
        
        [data-testid="stDataFrame"] thead th {
            color: #ffffff !important;
            background-color: #404040 !important;
        }
        
        [data-testid="stDataFrame"] tbody td {
            color: #ffffff !important;
            background-color: #2d2d2d !important;
        }
        
        table {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        table thead {
            background-color: #404040 !important;
        }
        
        table thead th {
            color: #ffffff !important;
            background-color: #404040 !important;
        }
        
        table tbody td {
            color: #ffffff !important;
            background-color: #2d2d2d !important;
        }
        
        /* Input fields */
        [data-testid="stTextInput"] input {
            background-color: #404040 !important;
            color: #ffffff !important;
            border: 1px solid #606060 !important;
        }
        
        [data-testid="stTextInput"] input::placeholder {
            color: #909090 !important;
        }
        
        /* Buttons */
        button {
            background-color: #2196F3 !important;
            color: #ffffff !important;
        }
        
        button:hover {
            background-color: #1976D2 !important;
        }
        
        /* Expanders */
        [data-testid="stExpander"] {
            background-color: #2d2d2d !important;
        }
        
        [data-testid="stExpander"] summary {
            color: #ffffff !important;
        }
        
        /* Info/Warning/Success messages */
        [data-testid="stAlert"] {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        [role="alert"] {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        /* Code blocks */
        pre {
            background-color: #1a1a1a !important;
            color: #e8e8e8 !important;
        }
        
        code {
            background-color: #2d2d2d !important;
            color: #e8e8e8 !important;
        }
        
        /* Charts and plots */
        [data-testid="stPlotlyContainer"] {
            background-color: #1e1e1e !important;
        }
        
        /* Divider */
        hr {
            border-color: #404040 !important;
        }
        
        /* Radio buttons and checkboxes */
        [data-testid="stRadio"] {
            color: #ffffff !important;
        }
        
        [data-testid="stCheckbox"] {
            color: #ffffff !important;
        }
        
        /* Logo background - keep white */
        [data-testid="stSidebar"] img {
            background-color: #ffffff !important;
            padding: 10px !important;
            border-radius: 5px !important;
        }
        
        /* Top header bar in dark mode */
        [data-testid="stAppViewContainer"] > section:first-child {
            background-color: #1e1e1e !important;
        }
        
        [data-testid="stAppViewContainer"] h1 {
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)

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
    
    # Theme Toggle
    st.subheader("🎨 Theme")
    theme_col1, theme_col2 = st.columns(2)
    
    with theme_col1:
        if st.button("☀️ Light", use_container_width=True, key="light_theme"):
            st.session_state.app_theme = "light"
            st.rerun()
    
    with theme_col2:
        if st.button("🌙 Dark", use_container_width=True, key="dark_theme"):
            st.session_state.app_theme = "dark"
            st.rerun()
    
    # Show current theme
    current_theme_display = "☀️ Light Mode" if st.session_state.app_theme == "light" else "🌙 Dark Mode"
    st.caption(f"Current: {current_theme_display}")
    
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
                    
                    # Extract and visualize tool outputs
                    if msg.get("steps"):
                        tool_outputs = extract_tool_outputs(msg.get("steps", []))
                        if tool_outputs:
                            # Show compact tool count badge
                            st.success(f"✓ Visualization ready ({len(tool_outputs)} tool{'s' if len(tool_outputs) != 1 else ''})")
                            render_tool_data_visualization(tool_outputs)
                        else:
                            st.warning("⚠️ No visualizations available for this response")
                    
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
    
    # ============ INPUT AREA (CHAT ONLY) ============
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
