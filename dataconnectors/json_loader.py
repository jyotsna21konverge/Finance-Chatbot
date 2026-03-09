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
    # Vendor Profile Data
    # =====================
    
    def get_profiles(self, vendor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get vendor profiles from profiles.json."""
        data = self._load_json_file("profiles.json")
        vendors = data.get("vendors", [])
        
        if vendor_id:
            return [v for v in vendors if v.get("vendor_id") == vendor_id]
        return vendors
    
    def search_profiles(self, search_field: str, search_value: Any) -> List[Dict[str, Any]]:
        """Search vendor profiles by any field."""
        vendors = self.get_profiles()
        return [v for v in vendors if v.get(search_field) == search_value]
    
    # =====================
    # AR Balance & Aging Data
    # =====================
    
    def get_balances(self, vendor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get AR aging report data from balances.json."""
        data = self._load_json_file("balances.json")
        balances = data.get("ar_balances", [])
        
        if vendor_id:
            return [b for b in balances if b.get("vendor_id") == vendor_id]
        return balances
    # =====================
    # Invoice/Transaction Data
    # =====================
    
    def get_transactions(
        self,
        vendor_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get invoices from transactions.json with optional filters."""
        data = self._load_json_file("transactions.json")
        invoices = data.get("invoices", [])
        
        # Apply filters
        if vendor_id:
            invoices = [i for i in invoices if i.get("vendor_id") == vendor_id]
        if status:
            invoices = [i for i in invoices if i.get("status") == status]
        
        # Return limited results
        return invoices[:limit]
    
    def search_transactions(
        self,
        search_field: str,
        search_value: Any,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search invoices by any field."""
        data = self._load_json_file("transactions.json")
        invoices = data.get("invoices", [])
        results = [i for i in invoices if i.get(search_field) == search_value]
        return results[:limit]
    
    # =====================
    # Vendor Credit Terms Data
    # =====================
    
    def get_credit_limits(self, vendor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get vendor credit terms from credit_limits.json."""
        data = self._load_json_file("credit_limits.json")
        vendors = data.get("vendors", [])
        
        if vendor_id:
            return [v for v in vendors if v.get("vendor_id") == vendor_id]
        return vendors
    
    def update_credit_limit(
        self,
        vendor_id: str,
        new_limit: float,
        adjustment_reason: str = "Manual adjustment",
    ) -> Dict[str, Any]:
        """Update credit limit for a vendor."""
        data = self._load_json_file("credit_limits.json")
        vendors = data.get("vendors", [])
        
        for vendor in vendors:
            if vendor.get("vendor_id") == vendor_id:
                old_limit = vendor.get("credit_limit")
                vendor["credit_limit"] = new_limit
                vendor["available_credit"] = new_limit - vendor.get("current_ar_balance", 0)
                vendor["utilization_percent"] = (
                    (vendor.get("current_ar_balance", 0) / new_limit * 100) if new_limit > 0 else 0
                )
                
                # Add to adjustment history
                if "adjustment_history" not in vendor:
                    vendor["adjustment_history"] = []
                
                adjustment = {
                    "adjustment_id": f"adj_{len(vendor['adjustment_history']) + 1:03d}",
                    "timestamp": "2026-03-05T00:00:00Z",
                    "previous_limit": old_limit,
                    "new_limit": new_limit,
                    "adjustment_type": "permanent",
                    "adjustment_reason": adjustment_reason,
                }
                vendor["adjustment_history"].append(adjustment)
                
                self._save_json_file("credit_limits.json", data)
                return {"ok": True, "message": f"Credit limit updated from {old_limit} to {new_limit}"}
        
        return {"ok": False, "error": f"Vendor {vendor_id} not found"}
    
    # =====================
    # AR Disputes Data
    # =====================
    
    def get_fraud_alerts(
        self,
        vendor_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get AR disputes and payment issues from fraud_alerts.json."""
        data = self._load_json_file("fraud_alerts.json")
        disputes = data.get("ar_disputes", [])
        
        if vendor_id:
            disputes = [d for d in disputes if d.get("vendor_id") == vendor_id]
        if status:
            disputes = [d for d in disputes if d.get("dispute_status") == status]
        
        return disputes[:limit]
    
    def get_fraud_alerts_by_employee(self, vendor_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get disputes for a specific vendor (AR-focused)."""
        return self.get_fraud_alerts(vendor_id=vendor_id, limit=limit)


# Global instance for easy access
json_loader = JSONDataLoader()
