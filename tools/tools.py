"""
JSON-based tools for financial data operations.
These tools interact with JSON files instead of a database.
"""

from typing import Any, Dict, List, Optional, Literal
from langchain.tools import tool
from dataconnectors.json_loader import json_loader


# =====================
# Profile/User Tools
# =====================

@tool("get_user_profile")
def get_user_profile(employee_id: str) -> Dict[str, Any]:
    """
    Get user profile information by employee ID.
    Returns profile details including role, department, and preferences.
    """
    if not employee_id or not isinstance(employee_id, str):
        return {"ok": False, "error": "employee_id must be a non-empty string"}
    
    try:
        profiles = json_loader.get_profiles(employee_id=employee_id)
        if profiles:
            return {"ok": True, "data": profiles[0]}
        return {"ok": False, "error": f"No profile found for employee_id: {employee_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("search_users")
def search_users(search_field: str, search_value: str) -> Dict[str, Any]:
    """
    Search for users by any field (e.g., name, email, role, department).
    
    Examples:
      search_field: "name", search_value: "Sarah Chen"
      search_field: "role", search_value: "Finance Manager"
      search_field: "department", search_value: "Finance"
    """
    if not search_field or not search_value:
        return {"ok": False, "error": "search_field and search_value are required"}
    
    try:
        results = json_loader.search_profiles(search_field, search_value)
        return {"ok": True, "count": len(results), "data": results}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Balance Tools
# =====================

@tool("get_account_balance")
def get_account_balance(account_id: Optional[str] = None, employee_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get account balance information.
    Provide either account_id or employee_id.
    
    Returns:
      - current_balance
      - available_balance
      - pending_charges
      - last_payment info
      - billing_cycle dates
    """
    try:
        if account_id:
            balances = json_loader.get_balances(account_id=account_id)
        elif employee_id:
            balances = json_loader.get_balance_by_employee(employee_id)
        else:
            return {"ok": False, "error": "Either account_id or employee_id is required"}
        
        if balances:
            return {"ok": True, "data": balances}
        return {"ok": False, "error": "No balance data found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_card_balance")
def get_card_balance(card_id: str) -> Dict[str, Any]:
    """
    Get balance information for a specific card.
    
    Returns:
      - current_balance
      - available_balance
      - pending_charges
      - last_payment details
    """
    if not card_id or not isinstance(card_id, str):
        return {"ok": False, "error": "card_id must be a non-empty string"}
    
    try:
        balance = json_loader.get_balance_by_card(card_id)
        if balance:
            return {"ok": True, "data": balance}
        return {"ok": False, "error": f"No balance found for card_id: {card_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Transaction Tools
# =====================

@tool("search_transactions")
def search_transactions(
    card_id: Optional[str] = None,
    employee_id: Optional[str] = None,
    status: Optional[Literal["approved", "denied", "pending"]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Search transactions with optional filters.
    
    Parameters:
      - card_id: Filter by card ID
      - employee_id: Filter by employee ID
      - status: Filter by transaction status (approved, denied, pending)
      - limit: Maximum number of results (default 50, max 500)
    
    Returns transaction list with merchant, amount, date, and status info.
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        transactions = json_loader.get_transactions(
            card_id=card_id,
            employee_id=employee_id,
            status=status,
            limit=limit
        )
        return {"ok": True, "count": len(transactions), "data": transactions}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_transaction_by_merchant")
def get_transaction_by_merchant(merchant_name: str, limit: int = 50) -> Dict[str, Any]:
    """
    Find all transactions for a specific merchant.
    """
    if not merchant_name or not isinstance(merchant_name, str):
        return {"ok": False, "error": "merchant_name must be a non-empty string"}
    
    try:
        transactions = json_loader.search_transactions("merchant", merchant_name, limit=limit)
        return {"ok": True, "count": len(transactions), "data": transactions}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_denied_transactions")
def get_denied_transactions(
    employee_id: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get all denied transactions, optionally filtered by employee.
    
    Returns:
      - transaction details with denial_reason and denial_category
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        transactions = json_loader.get_transactions(
            employee_id=employee_id,
            status="denied",
            limit=limit
        )
        return {"ok": True, "count": len(transactions), "data": transactions}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Credit Limit Tools
# =====================

@tool("get_credit_limits")
def get_credit_limits(employee_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """
    Get credit limit information for employees.
    
    Returns:
      - credit_limit
      - current_balance
      - available_credit
      - utilization_percent
      - status (at_limit, near_limit, normal)
      - adjustment_history
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        if employee_id:
            credits = json_loader.get_credit_limits(employee_id=employee_id)
        else:
            credits = json_loader.get_credit_limits()
        
        credits = credits[:limit]
        return {"ok": True, "count": len(credits), "data": credits}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_card_credit_limit")
def get_card_credit_limit(card_id: str) -> Dict[str, Any]:
    """
    Get credit limit information for a specific card.
    
    Returns:
      - credit_limit
      - available_credit
      - utilization_percent
      - status
    """
    if not card_id or not isinstance(card_id, str):
        return {"ok": False, "error": "card_id must be a non-empty string"}
    
    try:
        credit = json_loader.get_credit_limit_by_card(card_id)
        if credit:
            return {"ok": True, "data": credit}
        return {"ok": False, "error": f"No credit limit data for card_id: {card_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("update_credit_limit")
def update_credit_limit(
    card_id: str,
    new_limit: float,
    reason: str = "Manual adjustment",
) -> Dict[str, Any]:
    """
    Update the credit limit for a card.
    
    Automatically updates:
      - credit_limit
      - available_credit
      - utilization_percent
      - adjustment_history (appends record)
    """
    if not card_id or not isinstance(card_id, str):
        return {"ok": False, "error": "card_id must be a non-empty string"}
    
    if not isinstance(new_limit, (int, float)) or new_limit <= 0:
        return {"ok": False, "error": "new_limit must be a positive number"}
    
    try:
        result = json_loader.update_credit_limit(card_id, new_limit, reason)
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Fraud Alert Tools
# =====================

@tool("get_fraud_alerts")
def get_fraud_alerts(
    card_id: Optional[str] = None,
    investigation_status: Optional[Literal["investigating", "resolved", "false_positive"]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get fraud alerts from the system.
    
    Parameters:
      - card_id: Filter by card ID
      - investigation_status: Filter by status (investigating, resolved, false_positive)
      - limit: Maximum results
    
    Returns:
      - fraud_score
      - reason_codes (UNUSUAL_CATEGORY, UNUSUAL_TIME, HIGH_AMOUNT, etc.)
      - risk_factors
      - flagged_at timestamp
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        alerts = json_loader.get_fraud_alerts(
            card_id=card_id,
            status=investigation_status,
            limit=limit
        )
        return {"ok": True, "count": len(alerts), "data": alerts}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_fraud_alerts_by_employee")
def get_fraud_alerts_by_employee(employee_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get all fraud alerts for a specific employee.
    """
    if not employee_id or not isinstance(employee_id, str):
        return {"ok": False, "error": "employee_id must be a non-empty string"}
    
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        alerts = json_loader.get_fraud_alerts_by_employee(employee_id, limit=limit)
        return {"ok": True, "count": len(alerts), "data": alerts}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Fleet/Fuel Tools
# =====================

@tool("get_fleet_data")
def get_fleet_data(vehicle_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """
    Get fleet and fuel data for company vehicles.
    
    Returns:
      - vehicle details (make, model, year)
      - driver information
      - fuel card number
      - MPG data (current_mpg, average_mpg)
      - fuel costs (total_fuel_cost_ytd, total_gallons_ytd)
      - last fuel details
      - odometer reading
    """
    if limit <= 0 or limit > 500:
        return {"ok": False, "error": "limit must be between 1 and 500"}
    
    try:
        if vehicle_id:
            vehicles = json_loader.get_fleet_data(vehicle_id=vehicle_id)
        else:
            vehicles = json_loader.get_fleet_data()
        
        vehicles = vehicles[:limit]
        return {"ok": True, "count": len(vehicles), "data": vehicles}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_fleet_by_driver")
def get_fleet_by_driver(driver_id: str) -> Dict[str, Any]:
    """
    Get all vehicles assigned to a specific driver.
    """
    if not driver_id or not isinstance(driver_id, str):
        return {"ok": False, "error": "driver_id must be a non-empty string"}
    
    try:
        vehicles = json_loader.get_fleet_by_driver(driver_id)
        return {"ok": True, "count": len(vehicles), "data": vehicles}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("search_fleet")
def search_fleet(search_field: str, search_value: str) -> Dict[str, Any]:
    """
    Search fleet data by any field.
    
    Examples:
      search_field: "make", search_value: "Ford"
      search_field: "driver_name", search_value: "Robert Martinez"
      search_field: "department", search_value: "Sales"
      search_field: "status", search_value: "active"
    """
    if not search_field or not search_value:
        return {"ok": False, "error": "search_field and search_value are required"}
    
    try:
        results = json_loader.search_fleet(search_field, search_value)
        return {"ok": True, "count": len(results), "data": results}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# =====================
# Composite/Summary Tools
# =====================

@tool("get_employee_summary")
def get_employee_summary(employee_id: str) -> Dict[str, Any]:
    """
    Get a comprehensive summary for an employee including:
      - Profile information
      - All account balances
      - Recent transactions (last 20)
      - Credit limits
      - Any fraud alerts
      - Fleet assignments (if applicable)
    """
    if not employee_id or not isinstance(employee_id, str):
        return {"ok": False, "error": "employee_id must be a non-empty string"}
    
    try:
        summary = {
            "ok": True,
            "employee_id": employee_id,
            "data": {}
        }
        
        # Get profile
        profiles = json_loader.get_profiles(employee_id=employee_id)
        summary["data"]["profile"] = profiles[0] if profiles else None
        
        # Get balances
        summary["data"]["balances"] = json_loader.get_balance_by_employee(employee_id)
        
        # Get transactions
        summary["data"]["transactions"] = json_loader.get_transactions(
            employee_id=employee_id,
            limit=20
        )
        
        # Get credit limits
        credit_limits = json_loader.get_credit_limits(employee_id=employee_id)
        summary["data"]["credit_limits"] = credit_limits
        
        # Get fraud alerts
        summary["data"]["fraud_alerts"] = json_loader.get_fraud_alerts_by_employee(employee_id)
        
        # Get fleet assignments
        summary["data"]["fleet"] = json_loader.get_fleet_by_driver(employee_id)
        
        return summary
    except Exception as e:
        return {"ok": False, "error": str(e)}


@tool("get_high_risk_employees")
def get_high_risk_employees() -> Dict[str, Any]:
    """
    Identify high-risk employees based on:
      - Multiple fraud alerts (investigating status)
      - Credit limits at 100% utilization
      - Denied transactions
    
    Returns a list of employees with risk indicators.
    """
    try:
        high_risk = {}
        
        # Get all fraud alerts with investigating status
        fraud_alerts = json_loader.get_fraud_alerts(status="investigating", limit=500)
        
        # Get all credit limits at limit
        all_credits = json_loader.get_credit_limits()
        at_limit = [c for c in all_credits if c.get("utilization_percent", 0) >= 100]
        
        # Get denied transactions
        denied_txns = json_loader.get_transactions(status="denied", limit=500)
        
        # Aggregate by employee
        risk_employees = {}
        
        for alert in fraud_alerts:
            emp_id = alert.get("employee_id")
            if emp_id not in risk_employees:
                risk_employees[emp_id] = {"fraud_alerts": 0, "at_limit": False, "denied_txns": 0}
            risk_employees[emp_id]["fraud_alerts"] += 1
        
        for credit in at_limit:
            emp_id = credit.get("employee_id")
            if emp_id not in risk_employees:
                risk_employees[emp_id] = {"fraud_alerts": 0, "at_limit": False, "denied_txns": 0}
            risk_employees[emp_id]["at_limit"] = True
        
        for txn in denied_txns:
            emp_id = txn.get("employee_id")
            if emp_id not in risk_employees:
                risk_employees[emp_id] = {"fraud_alerts": 0, "at_limit": False, "denied_txns": 0}
            risk_employees[emp_id]["denied_txns"] += 1
        
        return {"ok": True, "high_risk_count": len(risk_employees), "data": risk_employees}
    except Exception as e:
        return {"ok": False, "error": str(e)}
