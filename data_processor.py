import pandas as pd
import numpy as np
from typing import Dict, Any

class DataProcessor:
    """Handles data import, cleaning, and analysis for healthcare visit data."""
    
    def __init__(self):
        self.required_columns = ['A', 'B', 'C', 'O']
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the imported data according to specifications:
        - Only retain rows where Column O contains 'verified' (case-insensitive)
        - Remove 'omit' entries completely
        - Strip whitespace from columns A, B, and C
        - Ignore columns E through R during processing
        """
        # Ensure we have the required columns
        if not all(col in df.columns for col in self.required_columns):
            # Try to map column positions if columns are named differently
            if len(df.columns) >= 15:  # Ensure we have at least columns A-O
                df = df.iloc[:, [0, 1, 2, 14]]  # Columns A, B, C, O (0-indexed)
                df.columns = ['A', 'B', 'C', 'O']
            else:
                raise ValueError("Required columns not found in the data")
        
        # Make a copy to avoid warnings
        working_df = df.copy()
        
        # Clean Column O and filter for 'verified' only
        if 'O' in working_df.columns:
            working_df['O'] = working_df['O'].astype(str).str.lower().str.strip()
            # Only keep rows where Column O contains 'verified'
            cleaned_df = working_df[working_df['O'] == 'verified'].copy()
        else:
            raise ValueError("Column O not found in the data")
        
        # Clean columns A, B, and C
        for col in ['A', 'B', 'C']:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        
        # Remove rows with null values in A, B, or C
        cleaned_df = cleaned_df.dropna(subset=['A', 'B', 'C'])
        
        # Remove rows where A, B, or C are empty after stripping
        cleaned_df = cleaned_df[
            (cleaned_df['A'] != '') & 
            (cleaned_df['B'] != '') & 
            (cleaned_df['C'] != '')
        ].copy()
        
        return cleaned_df
    
    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the cleaned data to count frequencies in each column.
        Returns a dictionary with analysis results for each category.
        """
        analysis_results = {}
        
        # Analyze Client Names (Column A)
        client_counts = df['A'].value_counts()
        analysis_results['client_analysis'] = client_counts.to_frame('count')
        
        # Analyze Employee Visits (Column B)
        employee_counts = df['B'].value_counts()
        analysis_results['employee_analysis'] = employee_counts.to_frame('count')
        
        # Analyze Services Provided (Column C)
        service_counts = df['C'].value_counts()
        analysis_results['service_analysis'] = service_counts.to_frame('count')
        
        return analysis_results
    
    def get_summary_statistics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from analysis results."""
        summary = {
            'total_unique_clients': len(analysis_results['client_analysis']),
            'total_client_visits': analysis_results['client_analysis']['count'].sum(),
            'total_unique_employees': len(analysis_results['employee_analysis']),
            'total_employee_visits': analysis_results['employee_analysis']['count'].sum(),
            'total_unique_services': len(analysis_results['service_analysis']),
            'total_service_instances': analysis_results['service_analysis']['count'].sum()
        }
        
        return summary
    
    def get_top_n(self, analysis_results: Dict[str, Any], n: int = 10) -> Dict[str, pd.DataFrame]:
        """Get top N results for each category."""
        top_results = {}
        
        for category, data in analysis_results.items():
            top_results[category] = data.head(n)
        
        return top_results