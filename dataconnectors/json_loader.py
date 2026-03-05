"""
JSON data loader for accessing financial data from JSON files.
Provides utilities to read, filter, and manipulate JSON data.
"""

import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path


class JSONDataLoader:
    """Load and access data from JSON files in the data folder."""
    
    def __init__(self, data_dir: str = "./data"):
        """Initialize the JSON data loader with a data directory path."""
        self.data_dir = Path(data_dir)
        self._data_cache: Dict[str, Any] = {}
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file from the data directory."""
        if filename in self._data_cache:
            return self._data_cache[filename]
        
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self._data_cache[filename] = data
                return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {str(e)}")
    
    def _save_json_file(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save data back to a JSON file."""
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            self._data_cache[filename] = data
            return True
        except Exception as e:
            raise IOError(f"Failed to save {filename}: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._data_cache.clear()
    
    # =====================
    # Profile Data
    # =====================
    
    def get_profiles(self, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user profiles from profiles.json."""
        data = self._load_json_file("profiles.json")
        users = data.get("users", [])
        
        if employee_id:
            return [u for u in users if u.get("employee_id") == employee_id]
        return users
    
    def search_profiles(self, search_field: str, search_value: Any) -> List[Dict[str, Any]]:
        """Search profiles by any field."""
        users = self.get_profiles()
        return [u for u in users if u.get(search_field) == search_value]
    
    # =====================
    # Balance Data
    # =====================
    
    def get_balances(self, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current balances from balances.json."""
        data = self._load_json_file("balances.json")
        balances = data.get("current_balances", [])
        
        if account_id:
            return [b for b in balances if b.get("account_id") == account_id]
        return balances
    
    def get_balance_by_employee(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get balance records for a specific employee."""
        balances = self.get_balances()
        return [b for b in balances if b.get("employee_id") == employee_id]
    
    def get_balance_by_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get balance for a specific card."""
        balances = self.get_balances()
        results = [b for b in balances if b.get("card_id") == card_id]
        return results[0] if results else None
    
    # =====================
    # Transaction Data
    # =====================
    
    def get_transactions(
        self,
        card_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get transactions from transactions.json with optional filters."""
        data = self._load_json_file("transactions.json")
        transactions = data.get("transactions", [])
        
        # Apply filters
        if card_id:
            transactions = [t for t in transactions if t.get("card_id") == card_id]
        if employee_id:
            transactions = [t for t in transactions if t.get("employee_id") == employee_id]
        if status:
            transactions = [t for t in transactions if t.get("status") == status]
        
        # Return limited results
        return transactions[:limit]
    
    def search_transactions(
        self,
        search_field: str,
        search_value: Any,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search transactions by any field."""
        data = self._load_json_file("transactions.json")
        transactions = data.get("transactions", [])
        results = [t for t in transactions if t.get(search_field) == search_value]
        return results[:limit]
    
    # =====================
    # Credit Limits Data
    # =====================
    
    def get_credit_limits(self, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get credit limits from credit_limits.json."""
        data = self._load_json_file("credit_limits.json")
        employees = data.get("employees", [])
        
        if employee_id:
            return [e for e in employees if e.get("employee_id") == employee_id]
        return employees
    
    def get_credit_limit_by_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get credit limit for a specific card."""
        employees = self.get_credit_limits()
        results = [e for e in employees if e.get("card_id") == card_id]
        return results[0] if results else None
    
    def update_credit_limit(
        self,
        card_id: str,
        new_limit: float,
        adjustment_reason: str = "Manual adjustment",
    ) -> Dict[str, Any]:
        """Update credit limit for a card."""
        data = self._load_json_file("credit_limits.json")
        employees = data.get("employees", [])
        
        for emp in employees:
            if emp.get("card_id") == card_id:
                old_limit = emp.get("credit_limit")
                emp["credit_limit"] = new_limit
                emp["available_credit"] = new_limit - emp.get("current_balance", 0)
                emp["utilization_percent"] = (
                    (emp.get("current_balance", 0) / new_limit * 100) if new_limit > 0 else 0
                )
                
                # Add to adjustment history
                if "adjustment_history" not in emp:
                    emp["adjustment_history"] = []
                
                adjustment = {
                    "adjustment_id": f"adj_{len(emp['adjustment_history']) + 1:03d}",
                    "timestamp": "2026-03-05T00:00:00Z",
                    "previous_limit": old_limit,
                    "new_limit": new_limit,
                    "adjustment_type": "permanent",
                    "adjustment_reason": adjustment_reason,
                }
                emp["adjustment_history"].append(adjustment)
                
                self._save_json_file("credit_limits.json", data)
                return {"ok": True, "message": f"Credit limit updated from {old_limit} to {new_limit}"}
        
        return {"ok": False, "error": f"Card {card_id} not found"}
    
    # =====================
    # Fraud Alerts Data
    # =====================
    
    def get_fraud_alerts(
        self,
        card_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get fraud alerts from fraud_alerts.json."""
        data = self._load_json_file("fraud_alerts.json")
        alerts = data.get("fraud_alerts", [])
        
        if card_id:
            alerts = [a for a in alerts if a.get("card_id") == card_id]
        if status:
            alerts = [a for a in alerts if a.get("investigation_status") == status]
        
        return alerts[:limit]
    
    def get_fraud_alerts_by_employee(self, employee_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get fraud alerts for a specific employee."""
        data = self._load_json_file("fraud_alerts.json")
        alerts = data.get("fraud_alerts", [])
        results = [a for a in alerts if a.get("employee_id") == employee_id]
        return results[:limit]
    
    # =====================
    # Fleet/Fuel Data
    # =====================
    
    def get_fleet_data(self, vehicle_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get fleet/fuel data from fleet_fuel.json."""
        data = self._load_json_file("fleet_fuel.json")
        vehicles = data.get("vehicles", [])
        
        if vehicle_id:
            return [v for v in vehicles if v.get("vehicle_id") == vehicle_id]
        return vehicles
    
    def get_fleet_by_driver(self, driver_id: str) -> List[Dict[str, Any]]:
        """Get fleet data for a specific driver."""
        vehicles = self.get_fleet_data()
        return [v for v in vehicles if v.get("driver_id") == driver_id]
    
    def search_fleet(self, search_field: str, search_value: Any) -> List[Dict[str, Any]]:
        """Search fleet data by any field."""
        vehicles = self.get_fleet_data()
        return [v for v in vehicles if v.get(search_field) == search_value]


# Global instance for easy access
json_loader = JSONDataLoader()
