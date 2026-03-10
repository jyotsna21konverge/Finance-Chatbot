"""
JSON-based tools for Accounts Receivable (AR) operations.
These tools interact with JSON files for vendor and invoice management.
"""

from typing import Any, Dict, List, Optional, Literal
from langchain.tools import tool
from dataconnectors.json_loader import json_loader


# =====================
# Vendor Profile Tools
# =====================

@tool("get_vendor_profile")
def get_vendor_profile(vendor_id: str) -> Dict[str, Any]:
    """
    Get vendor profile information by vendor ID.
    Returns vendor details including contact, payment terms, credit rating, and history.
    """
    if not vendor_id or not isinstance(vendor_id, str):
        return {"ok": False, "error": "vendor_id must be a non-empty string"}
    
    try:
        profiles = json_loader.get_profiles(vendor_id=vendor_id)
        if profiles:
            return {"ok": True, "data": profiles[0]}
        return {"ok": False, "error": f"No profile found for vendor_id: {vendor_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("search_vendors")
def search_vendors(search_field: str, search_value: str) -> Dict[str, Any]:
    """
    Search for vendors by any field (name, industry, status, credit_rating, payment_history, etc).
    
    Examples:
      search_field: "vendor_name", search_value: "TechSupply"
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

@tool("get_vendor_ar_balance")
def get_vendor_ar_balance(vendor_id: str) -> Dict[str, Any]:
    """
    Get AR aging report for a specific vendor.
    
    Returns:
      - ar_balance (total outstanding)
      - invoices_outstanding (count)
      - current_due
      - overdue_30, overdue_60, overdue_90 (aged buckets)
      - last_payment info
      - payment_terms and days_overdue
    """
    if not vendor_id or not isinstance(vendor_id, str):
        return {"ok": False, "error": "vendor_id must be a non-empty string"}
    
    try:
        balance = json_loader.get_balances(vendor_id=vendor_id)
        if balance:
            return {"ok": True, "data": balance}
        return {"ok": False, "error": f"No AR data found for vendor_id: {vendor_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_ar_aging_report")
def get_ar_aging_report(limit: int = 50) -> Dict[str, Any]:
    """
    Get comprehensive AR aging report for all vendors.
    
    Returns:
      - ar_balances for each vendor with age buckets
      - ar_summary with totals and percentages by aging bucket
      - vendors_at_risk count
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
    vendor_id: Optional[str] = None,
    status: Optional[Literal["current", "overdue", "paid"]] = None,
    payment_status: Optional[Literal["paid", "unpaid", "partial"]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Search invoices with optional filters.
    
    Parameters:
      - vendor_id: Filter by vendor
      - status: Filter by status (current, overdue, paid)
      - payment_status: Filter by payment status (paid, unpaid, partial)
      - limit: Maximum number of results
    
    Returns invoice list with amounts, dates, and status info.
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        invoices = json_loader.get_transactions(
            vendor_id=vendor_id,
            status=status,
            limit=limit
        )
        return {"ok": True, "count": len(invoices), "data": invoices}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_vendor_invoices")
def get_vendor_invoices(vendor_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get all invoices for a specific vendor.
    """
    if not vendor_id or not isinstance(vendor_id, str):
        return {"ok": False, "error": "vendor_id must be a non-empty string"}
    
    try:
        invoices = json_loader.get_transactions(vendor_id=vendor_id, limit=limit)
        return {"ok": True, "count": len(invoices), "data": invoices}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_overdue_invoices")
def get_overdue_invoices(
    vendor_id: Optional[str] = None,
    days_overdue: int = 0,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get all overdue invoices, optionally filtered by vendor.
    
    Parameters:
      - vendor_id: Optional filter by vendor
      - days_overdue: Filter invoices overdue by minimum X days (default 0)
      - limit: Maximum results
    
    Returns:
      - invoice details with days_overdue, amounts, and vendor info
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        invoices = json_loader.get_transactions(
            vendor_id=vendor_id,
            status="overdue",
            limit=limit
        )
        return {"ok": True, "count": len(invoices), "data": invoices}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Vendor Credit/Terms Tools
# =====================

@tool("get_vendor_credit_terms")
def get_vendor_credit_terms(vendor_id: str) -> Dict[str, Any]:
    """
    Get credit limit and payment terms for a specific vendor.
    
    Returns:
      - credit_limit
      - current_ar_balance
      - available_credit
      - utilization_percent
      - payment_terms
      - credit_rating
      - status
    """
    if not vendor_id or not isinstance(vendor_id, str):
        return {"ok": False, "error": "vendor_id must be a non-empty string"}
    
    try:
        credit = json_loader.get_credit_limits(vendor_id=vendor_id)
        if credit:
            return {"ok": True, "data": credit}
        return {"ok": False, "error": f"No credit terms data for vendor_id: {vendor_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_all_vendor_credit_terms")
def get_all_vendor_credit_terms(limit: int = 50) -> Dict[str, Any]:
    """
    Get credit terms for all vendors.
    
    Returns vendor credit information with utilization and ratings.
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
    vendor_id: Optional[str] = None,
    status: Optional[Literal["open", "investigating", "resolved", "escalated"]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get payment disputes and AR issues.
    
    Parameters:
      - vendor_id: Filter by vendor
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


@tool("get_vendor_disputes")
def get_vendor_disputes(vendor_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get all disputes for a specific vendor.
    """
    if not vendor_id or not isinstance(vendor_id, str):
        return {"ok": False, "error": "vendor_id must be a non-empty string"}
    
    try:
        disputes = json_loader.get_fraud_alerts_by_employee(vendor_id, limit=limit)
        return {"ok": True, "count": len(disputes), "data": disputes}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_critical_payment_issues")
def get_critical_payment_issues() -> Dict[str, Any]:
    """
    Get all critical payment issues and at-risk situations.
    
    Identifies vendors with:
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
# Vendor Summary/Analysis Tools
# =====================

@tool("get_vendor_summary")
def get_vendor_summary(vendor_id: str) -> Dict[str, Any]:
    """
    Get a comprehensive summary for a vendor including:
      - Vendor profile
      - AR aging report
      - Outstanding invoices (last 10)
      - Credit terms and utilization
      - Any payment disputes
      - Payment history
      - Status and risk indicators
    """
    if not vendor_id or not isinstance(vendor_id, str):
        return {"ok": False, "error": "vendor_id must be a non-empty string"}
    
    try:
        summary = {
            "ok": True,
            "vendor_id": vendor_id,
            "data": {}
        }
        
        # Get profile
        profiles = json_loader.get_profiles(vendor_id=vendor_id)
        summary["data"]["profile"] = profiles[0] if profiles else None
        
        # Get AR balance
        summary["data"]["ar_balance"] = json_loader.get_balances(vendor_id=vendor_id)
        
        # Get invoices
        summary["data"]["invoices"] = json_loader.get_transactions(
            vendor_id=vendor_id,
            limit=10
        )
        
        # Get credit terms
        credit_terms = json_loader.get_credit_limits(vendor_id=vendor_id)
        summary["data"]["credit_terms"] = credit_terms
        
        # Get disputes
        summary["data"]["disputes"] = json_loader.get_fraud_alerts_by_employee(vendor_id)
        
        return summary
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_at_risk_vendors")
def get_at_risk_vendors() -> Dict[str, Any]:
    """
    Identify at-risk vendors based on:
      - Multiple invoices overdue 60+ days
      - Unresolved disputes (escalated)
      - Credit limit utilization > 75%
      - Multiple payment issues
      - Payment history rating (poor/fair)
    
    Returns a list of vendors with risk indicators and recommended actions.
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
        risk_vendors = {}
        
        for balance in all_balances:
            vendor_id = balance.get("vendor_id")
            if balance.get("overdue_60", 0) > 0 or balance.get("overdue_90", 0) > 0:
                if vendor_id not in risk_vendors:
                    risk_vendors[vendor_id] = {
                        "vendor_name": balance.get("vendor_name"),
                        "risk_factors": [],
                        "total_overdue": 0
                    }
                risk_factors = risk_vendors[vendor_id]["risk_factors"]
                if balance.get("overdue_90", 0) > 0:
                    risk_factors.append(f"Invoices overdue 90+ days: ${balance.get('overdue_90', 0)}")
                if balance.get("overdue_60", 0) > 0:
                    risk_factors.append(f"Invoices overdue 60-90 days: ${balance.get('overdue_60', 0)}")
                risk_vendors[vendor_id]["total_overdue"] += balance.get("overdue_60", 0) + balance.get("overdue_90", 0)
        
        for credit in all_credits:
            vendor_id = credit.get("vendor_id")
            if credit.get("utilization_percent", 0) > 75:
                if vendor_id not in risk_vendors:
                    risk_vendors[vendor_id] = {
                        "vendor_name": credit.get("vendor_name"),
                        "risk_factors": [],
                        "total_overdue": 0
                    }
                risk_vendors[vendor_id]["risk_factors"].append(
                    f"High credit utilization: {credit.get('utilization_percent', 0)}%"
                )
        
        for dispute in all_disputes:
            vendor_id = dispute.get("vendor_id")
            if vendor_id not in risk_vendors:
                risk_vendors[vendor_id] = {
                    "vendor_name": dispute.get("vendor_name"),
                    "risk_factors": [],
                    "total_overdue": 0
                }
            risk_vendors[vendor_id]["risk_factors"].append("Escalated dispute on record")
        
        return {"ok": True, "at_risk_count": len(risk_vendors), "data": risk_vendors}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_ar_summary")
def get_ar_summary() -> Dict[str, Any]:
    """
    Get overall Accounts Receivable summary and key metrics.
    
    Returns:
      - Total AR balance
      - Current vs overdue breakdown
      - Vendors at risk count
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
        summary["data"]["high_risk_vendors"] = json_loader.get_fraud_alerts(
            status="escalated",
            limit=10
        )
        
        return summary
    except Exception as e:
        return {"ok": False, "error": str(e)}
