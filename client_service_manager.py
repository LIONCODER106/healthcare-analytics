"""
Client Service Hours Management System
Handles client-specific service hour configurations, period overrides, and historical tracking.
"""

import json
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
import os


class ClientServiceManager:
    """Manages client service hours with default configurations, period overrides, and historical tracking."""
    
    def __init__(self, clients_file: str = 'client_service_hours.json', history_file: str = 'client_hours_history.json'):
        self.clients_file = clients_file
        self.history_file = history_file
        self.clients_data = self._load_clients_data()
        self.history_data = self._load_history_data()
    
    def _load_clients_data(self) -> Dict[str, Dict[str, Any]]:
        """Load client service hours configuration from JSON file."""
        try:
            if os.path.exists(self.clients_file):
                with open(self.clients_file, 'r') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_clients_data(self):
        """Save client service hours configuration to JSON file."""
        try:
            with open(self.clients_file, 'w') as f:
                json.dump(self.clients_data, f, indent=2, default=self._json_serializer)
        except Exception as e:
            print(f"Error saving clients data: {e}")
    
    def _load_history_data(self) -> List[Dict[str, Any]]:
        """Load client service hours history from JSON file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_history_data(self):
        """Save client service hours history to JSON file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history_data, f, indent=2, default=self._json_serializer)
        except Exception as e:
            print(f"Error saving history data: {e}")
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for date objects."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return str(obj)
    
    def add_client(self, client_name: str, service_types: Dict[str, Dict[str, Any]]) -> bool:
        """
        Add a new client with their service hour configurations.
        
        Args:
            client_name: Name of the client
            service_types: Dictionary of service types with their configurations
                          Format: {"Home Health - Basic": {"default_hours": 20, "billing_method": "hourly", "rate": 41.45}}
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if client_name not in self.clients_data:
                self.clients_data[client_name] = {}
            
            # Add or update service types for the client
            for service_type, config in service_types.items():
                self.clients_data[client_name][service_type] = {
                    "default_hours": config.get("default_hours", 0),
                    "billing_method": config.get("billing_method", "hourly"),
                    "rate": config.get("rate", 0.0),
                    "created_date": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat()
                }
            
            self._save_clients_data()
            
            # Log the addition to history
            self._log_history(
                client_name=client_name,
                action="client_added",
                service_types=list(service_types.keys()),
                details=f"Client added with {len(service_types)} service types"
            )
            
            return True
        except Exception as e:
            print(f"Error adding client: {e}")
            return False
    
    def update_client_service_hours(self, client_name: str, service_type: str, new_hours: float, reason: str = "") -> bool:
        """
        Update default service hours for a client's service type.
        
        Args:
            client_name: Name of the client
            service_type: Type of service (e.g., "Home Health - Basic")
            new_hours: New default hours
            reason: Reason for the change
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if client_name not in self.clients_data:
                return False
            
            if service_type not in self.clients_data[client_name]:
                return False
            
            old_hours = self.clients_data[client_name][service_type]["default_hours"]
            self.clients_data[client_name][service_type]["default_hours"] = new_hours
            self.clients_data[client_name][service_type]["last_modified"] = datetime.now().isoformat()
            
            self._save_clients_data()
            
            # Log the change to history
            self._log_history(
                client_name=client_name,
                action="hours_updated",
                service_types=[service_type],
                old_value=old_hours,
                new_value=new_hours,
                reason=reason,
                details=f"Default hours changed from {old_hours} to {new_hours}"
            )
            
            return True
        except Exception as e:
            print(f"Error updating client service hours: {e}")
            return False
    
    def apply_period_override(self, client_name: str, service_type: str, override_hours: float, 
                            period_start: date, period_end: date, reason: str = "") -> bool:
        """
        Apply a temporary override for specific billing period.
        
        Args:
            client_name: Name of the client
            service_type: Type of service
            override_hours: Override hours for this period
            period_start: Start date of the period
            period_end: End date of the period
            reason: Reason for the override
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            default_hours = self.get_client_service_hours(client_name, service_type)
            if default_hours is None:
                return False
            
            # Log the override to history
            self._log_history(
                client_name=client_name,
                action="period_override",
                service_types=[service_type],
                old_value=default_hours,
                new_value=override_hours,
                period_start=period_start.isoformat(),
                period_end=period_end.isoformat(),
                reason=reason,
                details=f"Period override: {default_hours} → {override_hours} hours from {period_start} to {period_end}"
            )
            
            return True
        except Exception as e:
            print(f"Error applying period override: {e}")
            return False
    
    def get_client_service_hours(self, client_name: str, service_type: str) -> Optional[float]:
        """
        Get default service hours for a client's service type.
        
        Args:
            client_name: Name of the client
            service_type: Type of service
        
        Returns:
            float: Default hours if found, None otherwise
        """
        try:
            if client_name in self.clients_data and service_type in self.clients_data[client_name]:
                return self.clients_data[client_name][service_type]["default_hours"]
            return None
        except Exception:
            return None
    
    def get_client_service_config(self, client_name: str, service_type: str) -> Optional[Dict[str, Any]]:
        """
        Get complete service configuration for a client's service type.
        
        Args:
            client_name: Name of the client
            service_type: Type of service
        
        Returns:
            dict: Service configuration if found, None otherwise
        """
        try:
            if client_name in self.clients_data and service_type in self.clients_data[client_name]:
                return self.clients_data[client_name][service_type].copy()
            return None
        except Exception:
            return None
    
    def get_all_clients(self) -> List[str]:
        """Get list of all client names."""
        return list(self.clients_data.keys())
    
    def get_client_services(self, client_name: str) -> List[str]:
        """Get list of all service types for a client."""
        if client_name in self.clients_data:
            return list(self.clients_data[client_name].keys())
        return []
    
    def get_clients_summary(self) -> pd.DataFrame:
        """Get summary of all clients and their service configurations."""
        summary_data = []
        
        for client_name, services in self.clients_data.items():
            for service_type, config in services.items():
                summary_data.append({
                    "Client": client_name,
                    "Service Type": service_type,
                    "Default Hours": config["default_hours"],
                    "Billing Method": config["billing_method"],
                    "Rate": config["rate"],
                    "Created": config.get("created_date", ""),
                    "Last Modified": config.get("last_modified", "")
                })
        
        return pd.DataFrame(summary_data)
    
    def calculate_client_billing(self, client_name: str, service_analysis: Dict[str, int], 
                               period_overrides: Dict[str, float] = None) -> Dict[str, Dict[str, Any]]:
        """
        Calculate billing for a client based on their service hours and analysis data.
        
        Args:
            client_name: Name of the client
            service_analysis: Dictionary of service types and their counts/visits
            period_overrides: Optional dictionary of service types and override hours
        
        Returns:
            dict: Billing details for each service type
        """
        billing_results = {}
        period_overrides = period_overrides or {}
        
        for service_type, visit_count in service_analysis.items():
            config = self.get_client_service_config(client_name, service_type)
            if not config:
                continue
            
            # Use override hours if available, otherwise use default hours
            hours = period_overrides.get(service_type, config["default_hours"])
            rate = config["rate"]
            billing_method = config["billing_method"]
            
            if billing_method == "hourly":
                total_amount = hours * rate
                billing_results[service_type] = {
                    "hours": hours,
                    "rate": rate,
                    "billing_method": billing_method,
                    "total_amount": total_amount,
                    "visit_count": visit_count,
                    "is_override": service_type in period_overrides
                }
            else:
                # For future unit-based billing
                billing_results[service_type] = {
                    "units": hours,  # Will be converted to 15-min units later
                    "rate": rate,
                    "billing_method": billing_method,
                    "total_amount": hours * rate,
                    "visit_count": visit_count,
                    "is_override": service_type in period_overrides
                }
        
        return billing_results
    
    def _log_history(self, client_name: str, action: str, service_types: List[str], 
                    old_value: Any = None, new_value: Any = None, reason: str = "",
                    period_start: str = "", period_end: str = "", details: str = ""):
        """Log changes to client service hours history."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "client_name": client_name,
            "action": action,
            "service_types": service_types,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
            "period_start": period_start,
            "period_end": period_end,
            "details": details
        }
        
        self.history_data.append(history_entry)
        self._save_history_data()
    
    def get_client_history(self, client_name: str) -> List[Dict[str, Any]]:
        """Get history of changes for a specific client."""
        return [entry for entry in self.history_data if entry["client_name"] == client_name]
    
    def get_recent_history(self, n: int = 50) -> List[Dict[str, Any]]:
        """Get recent history entries."""
        return sorted(self.history_data, key=lambda x: x["timestamp"], reverse=True)[:n]
    
    def export_clients_data(self) -> str:
        """Export clients data as JSON string."""
        return json.dumps(self.clients_data, indent=2, default=self._json_serializer)
    
    def export_history_data(self) -> str:
        """Export history data as JSON string."""
        return json.dumps(self.history_data, indent=2, default=self._json_serializer)
    
    def delete_client(self, client_name: str) -> bool:
        """Delete a client and all their service configurations."""
        try:
            if client_name in self.clients_data:
                service_types = list(self.clients_data[client_name].keys())
                del self.clients_data[client_name]
                self._save_clients_data()
                
                # Log the deletion
                self._log_history(
                    client_name=client_name,
                    action="client_deleted",
                    service_types=service_types,
                    details=f"Client deleted with {len(service_types)} service types"
                )
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting client: {e}")
            return False
    
    def clear_all_data(self):
        """Clear all client data and history (use with caution)."""
        self.clients_data = {}
        self.history_data = []
        self._save_clients_data()
        self._save_history_data()