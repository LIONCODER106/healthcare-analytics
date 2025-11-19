import pandas as pd
import json
import os
from typing import Dict, Any

class FeeCalculator:
    """Handles service fee configuration and calculation."""
    
    def __init__(self, rates_file: str = 'service_rates.json'):
        self.rates_file = rates_file
        self.service_rates = self._load_service_rates()
    
    def _load_service_rates(self) -> Dict[str, Any]:
        """Load service rates from JSON file with support for different billing methods."""
        if os.path.exists(self.rates_file):
            try:
                with open(self.rates_file, 'r') as f:
                    rates = json.load(f)
                    # Convert old format to new format if needed
                    return self._convert_to_new_format(rates)
            except (json.JSONDecodeError, IOError):
                return self._get_default_rates()
        return self._get_default_rates()
    
    def _convert_to_new_format(self, rates: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old simple rates format to new structured format."""
        new_rates = {}
        for service, rate in rates.items():
            if isinstance(rate, (int, float)):
                # Old format - convert to new format
                if "Home Health - Basic" in service:
                    new_rates[service] = {
                        "rate": float(rate),
                        "billing_method": "hourly",
                        "unit": "hour"
                    }
                else:
                    new_rates[service] = {
                        "rate": float(rate),
                        "billing_method": "unit",
                        "unit": "15min"
                    }
            else:
                # Already new format
                new_rates[service] = rate
        return new_rates
    
    def _get_default_rates(self) -> Dict[str, Any]:
        """Get default service rates with new format."""
        return {
            "Home Health - Basic": {
                "rate": 41.45,
                "billing_method": "hourly",
                "unit": "hour"
            }
        }
    
    def _save_service_rates(self):
        """Save service rates to JSON file."""
        try:
            with open(self.rates_file, 'w') as f:
                json.dump(self.service_rates, f, indent=2)
        except IOError:
            pass  # Silently fail if unable to save
    
    def get_service_rates(self) -> Dict[str, float]:
        """Get current service rates."""
        return self.service_rates.copy()
    
    def update_service_rates(self, new_rates: Dict[str, float]):
        """Update service rates with new values."""
        self.service_rates.update(new_rates)
        self._save_service_rates()
    
    def set_service_rate(self, service: str, rate: float):
        """Set rate for a specific service."""
        self.service_rates[service] = rate
        self._save_service_rates()
    
    def calculate_fees(self, service_analysis: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate fees based on service analysis and configured rates.
        
        Args:
            service_analysis: DataFrame with service names as index and 'count' column
            
        Returns:
            DataFrame with service names, counts, rates, and total fees
        """
        if service_analysis.empty or not self.service_rates:
            return pd.DataFrame()
        
        # Create fee calculation DataFrame
        fee_data = []
        
        for service, row in service_analysis.iterrows():
            count = row['count']
            rate_data = self.service_rates.get(service, {})
            if isinstance(rate_data, dict):
                rate = rate_data.get('rate', 0.0)
            else:
                rate = rate_data if rate_data else 0.0
            total_fee = count * rate
            
            fee_data.append({
                'service': service,
                'count': count,
                'rate_per_service': rate,
                'total_fee': total_fee
            })
        
        fee_df = pd.DataFrame(fee_data)
        
        # Sort by total fee descending
        fee_df = fee_df.sort_values('total_fee', ascending=False)
        
        return fee_df
    
    def get_total_fees(self, service_analysis: pd.DataFrame) -> float:
        """Calculate total fees for all services."""
        fee_df = self.calculate_fees(service_analysis)
        return fee_df['total_fee'].sum() if not fee_df.empty else 0.0
    
    def get_fee_summary(self, service_analysis: pd.DataFrame) -> Dict[str, Any]:
        """Get a summary of fee calculations."""
        fee_df = self.calculate_fees(service_analysis)
        
        if fee_df.empty:
            return {
                'total_fees': 0.0,
                'average_fee_per_service': 0.0,
                'highest_fee_service': None,
                'lowest_fee_service': None,
                'services_with_rates': 0,
                'services_without_rates': len(service_analysis)
            }
        
        # Count services with and without rates
        services_with_rates = len(fee_df[fee_df['rate_per_service'] > 0])
        services_without_rates = len(fee_df[fee_df['rate_per_service'] == 0])
        
        summary = {
            'total_fees': fee_df['total_fee'].sum(),
            'average_fee_per_service': fee_df['total_fee'].mean(),
            'highest_fee_service': fee_df.loc[fee_df['total_fee'].idxmax(), 'service'] if not fee_df.empty else None,
            'lowest_fee_service': fee_df.loc[fee_df['total_fee'].idxmin(), 'service'] if not fee_df.empty else None,
            'services_with_rates': services_with_rates,
            'services_without_rates': services_without_rates
        }
        
        return summary
