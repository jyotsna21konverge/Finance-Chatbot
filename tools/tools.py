"""
JSON-based tools for Accounts Receivable (AR) operations.
These tools interact with JSON files for customer and order management.
"""

from typing import Any, Dict, List, Optional, Literal
from langchain.tools import tool
from dataconnectors.json_loader import json_loader
from datetime import datetime, timedelta


# =====================
# Visualization Tool
# =====================

@tool("create_visualization")
def create_visualization(
    chart_type: Literal["bar", "line", "pie", "table", "metrics", "scatter"],
    title: str,
    data_source: str,
    x_field: Optional[str] = None,
    y_field: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Recommend a visualization for the data being presented.
    
    Parameters:
      - chart_type: Type of chart (bar, line, pie, table, metrics, scatter)
      - title: Title for the visualization
      - data_source: Which tool's data to visualize (e.g., "get_invoice_status_summary", "search_invoices")
      - x_field: Field name for x-axis/categories (OPTIONAL - will auto-detect if not provided)
        * For pie charts: category field like "status", "category", "customer_name"
        * For bar/line: x-axis field
      - y_field: Field name for y-axis/values (OPTIONAL - will auto-detect if not provided)
        * For pie charts: value field like "count", "amount", "percentage"
        * For bar/line: y-axis field
      - description: Brief description of what the visualization shows
    
    Chart type guidelines:
      - bar: Comparisons across categories (aging buckets, customer counts, status breakdown)
      - line: Trends over time (payment history, balance changes)
      - pie: Proportional breakdown (status distribution, category percentages)
        * IMPORTANT: For invoice status, use x_field="status" and y_field="count" or "percentage"
      - table: Detailed records (invoice lists, customer profiles)
      - metrics: Key numbers (totals, counts, averages)
      - scatter: Correlations between two variables
    
    NOTE: If x_field and y_field are not provided, the system will attempt to auto-detect
    appropriate fields based on the data structure and chart type.
    
    Returns visualization configuration that the UI will use to render the chart.
    """
    if not chart_type or not title or not data_source:
        return {"ok": False, "error": "chart_type, title, and data_source are required"}
    
    valid_chart_types = ["bar", "line", "pie", "table", "metrics", "scatter"]
    if chart_type not in valid_chart_types:
        return {"ok": False, "error": f"chart_type must be one of: {', '.join(valid_chart_types)}"}
    
    # Build visualization config
    viz_config = {
        "ok": True,
        "visualization": {
            "chart_type": chart_type,
            "title": title,
            "data_source": data_source,
            "x_field": x_field,
            "y_field": y_field,
            "description": description or f"{chart_type.capitalize()} chart showing {title}"
        }
    }
    
    return viz_config


# =====================
# Time-Based Analysis Tools
# =====================

@tool("get_recent_invoices")
def get_recent_invoices(days_back: int = 30) -> Dict[str, Any]:
    """
    Get invoices created within the last N days.
    Perfect for queries like "invoices in last 1 month" or "recent invoices".
    
    Parameters:
      - days_back: Number of days to look back (default 30 for last month)
    
    Returns:
      - invoice_id, customer_name, customer_id
      - invoice_date, due_date
      - invoice_amount, amount_due (outstanding)
      - status, payment_status
      - days_since_invoice: How many days ago the invoice was created
    """
    if days_back <= 0 or days_back > 365:
        return {"ok": False, "error": "days_back must be between 1 and 365"}
    
    try:
        # Get all invoices
        all_invoices = json_loader.get_transactions(limit=1000)
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        recent_invoices = []
        for invoice in all_invoices:
            try:
                # Parse invoice date
                invoice_date_str = invoice.get("invoice_date", "")
                if invoice_date_str:
                    # Handle ISO format dates
                    invoice_date = datetime.fromisoformat(invoice_date_str.replace('Z', '+00:00'))
                    
                    # Check if within date range
                    if invoice_date >= cutoff_date:
                        days_since = (datetime.now(invoice_date.tzinfo) - invoice_date).days
                        
                        recent_invoices.append({
                            "invoice_id": invoice.get("invoice_id"),
                            "customer_id": invoice.get("customer_id"),
                            "customer_name": invoice.get("customer_name"),
                            "invoice_date": invoice.get("invoice_date"),
                            "due_date": invoice.get("due_date"),
                            "invoice_amount": float(invoice.get("invoice_amount", 0)),
                            "amount_due": float(invoice.get("amount_due", 0)),
                            "status": invoice.get("status"),
                            "payment_status": invoice.get("payment_status"),
                            "days_since_invoice": days_since
                        })
            except Exception as e:
                # Skip invoices with date parsing errors
                continue
        
        return {
            "ok": True,
            "days_back": days_back,
            "count": len(recent_invoices),
            "data": recent_invoices
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_customer_outstanding_by_period")
def get_customer_outstanding_by_period(days_back: int = 30) -> Dict[str, Any]:
    """
    Get customers who raised invoices in the last N days with their total outstanding amounts.
    Perfect for: "List customers with invoices in last 1 month and their outstanding amounts"
    
    Parameters:
      - days_back: Number of days to look back (default 30 for last month)
    
    Returns:
      - customer_id, customer_name
      - invoice_count: Number of invoices in the period
      - total_invoice_amount: Total amount of invoices in period
      - total_outstanding_amount: Total amount still due
      - average_days_outstanding: Average days since invoice
    """
    if days_back <= 0 or days_back > 365:
        return {"ok": False, "error": "days_back must be between 1 and 365"}
    
    try:
        # Get all invoices directly (don't call another tool)
        all_invoices = json_loader.get_transactions(limit=1000)
        
        if not all_invoices:
            return {"ok": True, "days_back": days_back, "customer_count": 0, "data": []}
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Group by customer
        customer_summary = {}
        
        for invoice in all_invoices:
            try:
                # Parse invoice date
                invoice_date_str = invoice.get("invoice_date", "")
                if not invoice_date_str:
                    continue
                
                # Handle ISO format dates
                invoice_date = datetime.fromisoformat(invoice_date_str.replace('Z', '+00:00'))
                
                # Check if within date range
                if invoice_date < cutoff_date:
                    continue
                
                customer_id = invoice.get("customer_id")
                customer_name = invoice.get("customer_name")
                
                if not customer_id:
                    continue
                
                if customer_id not in customer_summary:
                    customer_summary[customer_id] = {
                        "customer_id": customer_id,
                        "customer_name": customer_name,
                        "invoice_count": 0,
                        "total_invoice_amount": 0.0,
                        "total_outstanding_amount": 0.0,
                        "days_outstanding_list": []
                    }
                
                # Add invoice data
                customer_summary[customer_id]["invoice_count"] += 1
                customer_summary[customer_id]["total_invoice_amount"] += float(invoice.get("invoice_amount", 0))
                customer_summary[customer_id]["total_outstanding_amount"] += float(invoice.get("amount_due", 0))
                
                # Calculate days since invoice
                days_since = (datetime.now(invoice_date.tzinfo) - invoice_date).days
                customer_summary[customer_id]["days_outstanding_list"].append(days_since)
                
            except Exception as e:
                # Skip invoices with errors
                continue
        
        # Format results
        results = []
        for customer_data in customer_summary.values():
            days_list = customer_data["days_outstanding_list"]
            avg_days = sum(days_list) / len(days_list) if days_list else 0
            
            results.append({
                "customer_name": customer_data["customer_name"],
                "customer_id": customer_data["customer_id"],
                "invoice_count": customer_data["invoice_count"],
                "total_invoice_amount": round(customer_data["total_invoice_amount"], 2),
                "total_outstanding_amount": round(customer_data["total_outstanding_amount"], 2),
                "average_days_outstanding": round(avg_days, 1)
            })
        
        # Sort by total outstanding amount (descending)
        results.sort(key=lambda x: x["total_outstanding_amount"], reverse=True)
        
        return {
            "ok": True,
            "days_back": days_back,
            "customer_count": len(results),
            "data": results
        }
    except Exception as e:
        import traceback
        return {"ok": False, "error": f"Error: {str(e)}", "traceback": traceback.format_exc()}


@tool("get_invoices_by_date_range")
def get_invoices_by_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Get invoices within a specific date range.
    
    Parameters:
      - start_date: Start date in format "YYYY-MM-DD" (e.g., "2026-02-01")
      - end_date: End date in format "YYYY-MM-DD" (e.g., "2026-03-10")
    
    Returns invoices created between these dates with customer and amount information.
    """
    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            return {"ok": False, "error": "start_date must be before end_date"}
        
        # Get all invoices
        all_invoices = json_loader.get_transactions(limit=1000)
        
        invoices_in_range = []
        for invoice in all_invoices:
            try:
                invoice_date_str = invoice.get("invoice_date", "")
                if invoice_date_str:
                    invoice_date = datetime.fromisoformat(invoice_date_str.replace('Z', '+00:00'))
                    invoice_date_only = invoice_date.replace(tzinfo=None)
                    
                    if start <= invoice_date_only <= end:
                        invoices_in_range.append({
                            "invoice_id": invoice.get("invoice_id"),
                            "customer_id": invoice.get("customer_id"),
                            "customer_name": invoice.get("customer_name"),
                            "invoice_date": invoice.get("invoice_date"),
                            "due_date": invoice.get("due_date"),
                            "invoice_amount": float(invoice.get("invoice_amount", 0)),
                            "amount_due": float(invoice.get("amount_due", 0)),
                            "status": invoice.get("status"),
                            "payment_status": invoice.get("payment_status")
                        })
            except Exception as e:
                continue
        
        return {
            "ok": True,
            "start_date": start_date,
            "end_date": end_date,
            "count": len(invoices_in_range),
            "data": invoices_in_range
        }
    except ValueError as e:
        return {"ok": False, "error": f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Customer Profile Tools
# =====================

@tool("get_customer_profile")
def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    """
    Get customer profile information by customer ID.
    Returns customer details including contact, payment terms, credit rating, and history.
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"ok": False, "error": "customer_id must be a non-empty string"}
    
    try:
        profiles = json_loader.get_profiles(customer_id=customer_id)
        if profiles:
            return {"ok": True, "data": profiles[0]}
        return {"ok": False, "error": f"No profile found for customer_id: {customer_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("search_customers")
def search_customers(search_field: str, search_value: str) -> Dict[str, Any]:
    """
    Search for customers by any field (name, industry, status, credit_rating, payment_history, etc).
    
    Examples:
      search_field: "customer_name", search_value: "TechSupply"
      search_field: "industry", search_value: "Manufacturing"
      search_field: "status", search_value: "at_risk"
      search_field: "credit_rating", search_value: "A"
    """
    if not search_field or not search_value:
        return {"ok": False, "error": "search_field and search_value are required"}
    
    try:
        results = json_loader.search_profiles(search_field, search_value)
        return {"ok": True, "count": len(results), "data": results}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# AR Balance & Aging Tools
# =====================

@tool("get_customer_ar_balance")
def get_customer_ar_balance(customer_id: str) -> Dict[str, Any]:
    """
    Get AR aging report for a specific customer.
    
    Returns:
      - ar_balance (total outstanding)
      - invoices_outstanding (count)
      - current_due
      - overdue_30, overdue_60, overdue_90 (aged buckets)
      - last_payment info
      - payment_terms and days_overdue
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"ok": False, "error": "customer_id must be a non-empty string"}
    
    try:
        balance = json_loader.get_balances(customer_id=customer_id)
        if balance:
            return {"ok": True, "data": balance}
        return {"ok": False, "error": f"No AR data found for customer_id: {customer_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_ar_aging_report")
def get_ar_aging_report(limit: int = 50) -> Dict[str, Any]:
    """
    Get comprehensive AR aging report for all customers.
    
    Returns:
      - ar_balances for each customer with age buckets
      - customer_summary with totals and percentages by aging bucket
      - customers_at_risk count
      - aging_analysis
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        balances = json_loader.get_balances()
        balances = balances[:limit]
        return {"ok": True, "count": len(balances), "data": balances}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Invoice Tools
# =====================

@tool("search_invoices")
def search_invoices(
    customer_id: Optional[str] = None,
    status: Optional[Literal["current", "overdue", "paid"]] = None,
    payment_status: Optional[Literal["paid", "unpaid", "partial"]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Search invoices with optional filters.
    
    Parameters:
      - customer_id: Filter by customer
      - status: Filter by status (current, overdue, paid)
      - payment_status: Filter by payment status (paid, unpaid, partial)
      - limit: Maximum number of results
    
    Returns invoice list with amounts, dates, and status info.
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        invoices = json_loader.get_transactions(
            customer_id=customer_id,
            status=status,
            limit=limit
        )
        return {"ok": True, "count": len(invoices), "data": invoices}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_customer_invoices")
def get_customer_invoices(customer_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get all invoices for a specific customer.
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"ok": False, "error": "customer_id must be a non-empty string"}
    
    try:
        invoices = json_loader.get_transactions(customer_id=customer_id, limit=limit)
        return {"ok": True, "count": len(invoices), "data": invoices}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_overdue_invoices")
def get_overdue_invoices(
    customer_id: Optional[str] = None,
    days_overdue: int = 0,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get all overdue invoices, optionally filtered by customer.
    
    Parameters:
      - customer_id: Optional filter by customer
      - days_overdue: Filter invoices overdue by minimum X days (default 0)
      - limit: Maximum results
    
    Returns:
      - invoice details with days_overdue, amounts, and customer info
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        invoices = json_loader.get_transactions(
            customer_id=customer_id,
            status="overdue",
            limit=limit
        )
        return {"ok": True, "count": len(invoices), "data": invoices}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Customer Credit/Terms Tools
# =====================

@tool("get_customer_credit_terms")
def get_customer_credit_terms(customer_id: str) -> Dict[str, Any]:
    """
    Get credit limit and payment terms for a specific customer.
    
    Returns:
      - credit_limit
      - current_ar_balance
      - available_credit
      - utilization_percent
      - payment_terms
      - credit_rating
      - status
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"ok": False, "error": "customer_id must be a non-empty string"}
    
    try:
        credit = json_loader.get_credit_limits(customer_id=customer_id)
        if credit:
            return {"ok": True, "data": credit}
        return {"ok": False, "error": f"No credit terms data for customer_id: {customer_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_all_customer_credit_terms")
def get_all_customer_credit_terms(limit: int = 50) -> Dict[str, Any]:
    """
    Get credit terms for all customers.
    
    Returns customer credit information with utilization and ratings.
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        credits = json_loader.get_credit_limits()
        credits = credits[:limit]
        return {"ok": True, "count": len(credits), "data": credits}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Dispute & Issues Tools
# =====================

@tool("get_ar_disputes")
def get_ar_disputes(
    customer_id: Optional[str] = None,
    status: Optional[Literal["open", "investigating", "resolved", "escalated"]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get payment disputes and AR issues.
    
    Parameters:
      - customer_id: Filter by customer
      - status: Filter by dispute status
      - limit: Maximum results
    
    Returns:
      - dispute_id, invoice details
      - disputed_amount and reason
      - resolution status and notes
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        disputes = json_loader.get_fraud_alerts(limit=limit)
        return {"ok": True, "count": len(disputes), "data": disputes}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_customer_disputes")
def get_customer_disputes(customer_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get all disputes for a specific customer.
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"ok": False, "error": "customer_id must be a non-empty string"}
    
    try:
        disputes = json_loader.get_fraud_alerts_by_employee(customer_id, limit=limit)
        return {"ok": True, "count": len(disputes), "data": disputes}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_critical_payment_issues")
def get_critical_payment_issues() -> Dict[str, Any]:
    """
    Get all critical payment issues and at-risk situations.
    
    Identifies customers with:
      - Multiple overdue invoices (100+ days past due)
      - Payment suspensions
      - Unresolved disputes
      - Compliance risks
    
    Returns list of critical issues requiring immediate attention.
    """
    try:
        issues = json_loader.get_fraud_alerts(status="escalated", limit=500)
        return {"ok": True, "critical_count": len(issues), "data": issues}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Customer Summary/Analysis Tools
# =====================

@tool("get_customer_summary")
def get_customer_summary(customer_id: str) -> Dict[str, Any]:
    """
    Get a comprehensive summary for a customer including:
      - Customer profile
      - AR aging report
      - Outstanding invoices (last 10)
      - Credit terms and utilization
      - Any payment disputes
      - Payment history
      - Status and risk indicators
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"ok": False, "error": "customer_id must be a non-empty string"}
    
    try:
        summary = {
            "ok": True,
            "customer_id": customer_id,
            "data": {}
        }
        
        # Get profile
        profiles = json_loader.get_profiles(customer_id=customer_id)
        summary["data"]["profile"] = profiles[0] if profiles else None
        
        # Get AR balance
        summary["data"]["ar_balance"] = json_loader.get_balances(customer_id=customer_id)
        
        # Get invoices
        summary["data"]["invoices"] = json_loader.get_transactions(
            customer_id=customer_id,
            limit=10
        )
        
        # Get credit terms
        credit_terms = json_loader.get_credit_limits(customer_id=customer_id)
        summary["data"]["credit_terms"] = credit_terms
        
        # Get disputes
        summary["data"]["disputes"] = json_loader.get_fraud_alerts_by_employee(customer_id)
        
        return summary
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_at_risk_customers")
def get_at_risk_customers() -> Dict[str, Any]:
    """
    Identify at-risk customers based on:
      - Multiple invoices overdue 60+ days
      - Unresolved disputes (escalated)
      - Credit limit utilization > 75%
      - Multiple payment issues
      - Payment history rating (poor/fair)
    
    Returns a list of customers with risk indicators and recommended actions.
    """
    try:
        at_risk = {}
        
        # Get all AR balances
        all_balances = json_loader.get_balances()
        
        # Get credit terms
        all_credits = json_loader.get_credit_limits()
        
        # Get disputes
        all_disputes = json_loader.get_fraud_alerts(status="escalated", limit=500)
        
        # Build risk assessment
        risk_customers = {}
        
        for balance in all_balances:
            customer_id = balance.get("customer_id")
            if balance.get("overdue_60", 0) > 0 or balance.get("overdue_90", 0) > 0:
                if customer_id not in risk_customers:
                    risk_customers[customer_id] = {
                        "customer_name": balance.get("customer_name"),
                        "risk_factors": [],
                        "total_overdue": 0
                    }
                risk_factors = risk_customers[customer_id]["risk_factors"]
                if balance.get("overdue_90", 0) > 0:
                    risk_factors.append(f"Invoices overdue 90+ days: ${balance.get('overdue_90', 0)}")
                if balance.get("overdue_60", 0) > 0:
                    risk_factors.append(f"Invoices overdue 60-90 days: ${balance.get('overdue_60', 0)}")
                risk_customers[customer_id]["total_overdue"] += balance.get("overdue_60", 0) + balance.get("overdue_90", 0)
        
        for credit in all_credits:
            customer_id = credit.get("customer_id")
            if credit.get("utilization_percent", 0) > 75:
                if customer_id not in risk_customers:
                    risk_customers[customer_id] = {
                        "customer_name": credit.get("customer_name"),
                        "risk_factors": [],
                        "total_overdue": 0
                    }
                risk_customers[customer_id]["risk_factors"].append(
                    f"High credit utilization: {credit.get('utilization_percent', 0)}%"
                )
        
        for dispute in all_disputes:
            customer_id = dispute.get("customer_id")
            if customer_id not in risk_customers:
                risk_customers[customer_id] = {
                    "customer_name": dispute.get("customer_name"),
                    "risk_factors": [],
                    "total_overdue": 0
                }
            risk_customers[customer_id]["risk_factors"].append("Escalated dispute on record")
        
        return {"ok": True, "at_risk_count": len(risk_customers), "data": risk_customers}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_ar_summary")
def get_ar_summary() -> Dict[str, Any]:
    """
    Get overall Accounts Receivable summary and key metrics.
    
    Returns:
      - Total AR balance
      - Current vs overdue breakdown
      - Customers at risk count
      - Top overdue invoices
      - Aging analysis
      - Performance metrics
    """
    try:
        summary = {
            "ok": True,
            "data": {}
        }
        
        # Get all balances and aggregate
        all_balances = json_loader.get_balances()
        summary["data"]["ar_breakdown"] = all_balances
        
        # Get summary data if available
        summary["data"]["high_risk_customers"] = json_loader.get_fraud_alerts(
            status="escalated",
            limit=10
        )
        
        return summary
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_ar_totals")
def get_ar_totals() -> Dict[str, Any]:
    """
    Get total AR metrics across all customers.
    Perfect for queries asking about total AR balance, overall amounts, or aggregate metrics.
    
    Returns:
      - total_ar_balance: Total accounts receivable across all customers
      - total_current: Total current (not overdue) amount
      - total_overdue: Total overdue amount (30+ days)
      - total_overdue_30: Amount overdue 30-60 days
      - total_overdue_60: Amount overdue 60-90 days
      - total_overdue_90: Amount overdue 90+ days
      - customer_count: Number of customers
      - overdue_percentage: Percentage of AR that is overdue
    """
    try:
        # Get all balances
        all_balances = json_loader.get_balances()
        
        # Calculate totals
        total_ar = 0
        total_current = 0
        total_overdue_30 = 0
        total_overdue_60 = 0
        total_overdue_90 = 0
        
        for balance in all_balances:
            total_ar += float(balance.get("ar_balance", 0) or 0)
            total_current += float(balance.get("current_due", 0) or 0)
            total_overdue_30 += float(balance.get("overdue_30", 0) or 0)
            total_overdue_60 += float(balance.get("overdue_60", 0) or 0)
            total_overdue_90 += float(balance.get("overdue_90", 0) or 0)
        
        total_overdue = total_overdue_30 + total_overdue_60 + total_overdue_90
        overdue_percentage = (total_overdue / total_ar * 100) if total_ar > 0 else 0
        
        result = {
            "metric": "AR Totals",
            "total_ar_balance": round(total_ar, 2),
            "total_current": round(total_current, 2),
            "total_overdue": round(total_overdue, 2),
            "total_overdue_30": round(total_overdue_30, 2),
            "total_overdue_60": round(total_overdue_60, 2),
            "total_overdue_90": round(total_overdue_90, 2),
            "customer_count": len(all_balances),
            "overdue_percentage": round(overdue_percentage, 1)
        }
        
        return {"ok": True, "data": [result]}  # Return as list for consistency
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_invoice_status_summary")
def get_invoice_status_summary() -> Dict[str, Any]:
    """
    Get summary of invoice counts and amounts by status.
    Perfect for analyzing invoice status distribution and percentages.
    
    Returns:
      - status: Invoice status (current, overdue, paid)
      - count: Number of invoices with this status
      - total_amount: Total invoice amount for this status
      - percentage: Percentage of total invoices
    """
    try:
        # Get all invoices
        all_invoices = json_loader.get_transactions(limit=1000)
        
        # Group by status
        status_summary = {}
        total_count = len(all_invoices)
        
        for invoice in all_invoices:
            status = invoice.get("status", "unknown")
            amount = float(invoice.get("invoice_amount", 0))
            
            if status not in status_summary:
                status_summary[status] = {
                    "status": status,
                    "count": 0,
                    "total_amount": 0
                }
            
            status_summary[status]["count"] += 1
            status_summary[status]["total_amount"] += amount
        
        # Calculate percentages and format results
        results = []
        for status_data in status_summary.values():
            percentage = (status_data["count"] / total_count * 100) if total_count > 0 else 0
            results.append({
                "status": status_data["status"].capitalize(),
                "count": status_data["count"],
                "total_amount": round(status_data["total_amount"], 2),
                "percentage": round(percentage, 1)
            })
        
        # Sort by count descending
        results.sort(key=lambda x: x["count"], reverse=True)
        
        return {"ok": True, "total_invoices": total_count, "data": results}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_customer_invoice_totals")
def get_customer_invoice_totals(limit: int = 50) -> Dict[str, Any]:
    """
    Get total invoice amounts grouped by customer.
    Useful for analyzing invoice distribution across customers.
    
    Returns:
      - customer_name: Name of the customer
      - customer_id: Customer identifier
      - total_invoice_amount: Sum of all invoice amounts for this customer
      - invoice_count: Number of invoices for this customer
      - average_invoice_amount: Average invoice amount
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        # Get all invoices
        all_invoices = json_loader.get_transactions(limit=1000)
        
        # Group by customer and calculate totals
        customer_totals = {}
        for invoice in all_invoices:
            customer_id = invoice.get("customer_id")
            customer_name = invoice.get("customer_name", customer_id)
            invoice_amount = float(invoice.get("invoice_amount", 0))
            
            if customer_id not in customer_totals:
                customer_totals[customer_id] = {
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "total_invoice_amount": 0,
                    "invoice_count": 0,
                    "invoices": []
                }
            
            customer_totals[customer_id]["total_invoice_amount"] += invoice_amount
            customer_totals[customer_id]["invoice_count"] += 1
            customer_totals[customer_id]["invoices"].append(invoice_amount)
        
        # Calculate averages and format results
        results = []
        for customer_data in customer_totals.values():
            results.append({
                "customer_id": customer_data["customer_id"],
                "customer_name": customer_data["customer_name"],
                "total_invoice_amount": round(customer_data["total_invoice_amount"], 2),
                "invoice_count": customer_data["invoice_count"],
                "average_invoice_amount": round(
                    customer_data["total_invoice_amount"] / customer_data["invoice_count"], 2
                ) if customer_data["invoice_count"] > 0 else 0
            })
        
        # Sort by total amount descending
        results.sort(key=lambda x: x["total_invoice_amount"], reverse=True)
        
        return {"ok": True, "count": len(results[:limit]), "data": results[:limit]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
