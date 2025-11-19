import pandas as pd
import io
from typing import Any

def export_to_csv(df: pd.DataFrame) -> str:
    """Convert DataFrame to CSV string for download."""
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Format a number as currency."""
    return f"{currency_symbol}{amount:,.2f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format a decimal as percentage."""
    return f"{value * 100:.{decimal_places}f}%"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator

def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to a maximum length with optional suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def validate_file_type(filename: str, allowed_extensions: list = ['.csv', '.xlsm', '.xlsx']) -> bool:
    """Validate if a file has an allowed extension."""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)

def clean_column_name(column_name: str) -> str:
    """Clean and standardize column names."""
    # Remove extra whitespace and convert to lowercase
    cleaned = str(column_name).strip().lower()
    
    # Replace spaces and special characters with underscores
    import re
    cleaned = re.sub(r'[^\w\s]', '_', cleaned)
    cleaned = re.sub(r'\s+', '_', cleaned)
    
    # Remove multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    return cleaned

def get_file_size_mb(file_obj: Any) -> float:
    """Get file size in megabytes."""
    try:
        file_obj.seek(0, 2)  # Seek to end
        size_bytes = file_obj.tell()
        file_obj.seek(0)  # Reset to beginning
        return size_bytes / (1024 * 1024)
    except:
        return 0.0

def create_summary_stats(df: pd.DataFrame) -> dict:
    """Create summary statistics for a DataFrame."""
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'null_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum()
    }

def format_number(number: float, decimal_places: int = 0) -> str:
    """Format a number with thousands separators."""
    if decimal_places == 0:
        return f"{number:,.0f}"
    else:
        return f"{number:,.{decimal_places}f}"

def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate between two values."""
    if previous == 0:
        return 0.0
    return (current - previous) / previous

def get_top_n_percent(df: pd.DataFrame, column: str, n_percent: float = 0.1) -> pd.DataFrame:
    """Get top N percent of rows based on a column value."""
    threshold = df[column].quantile(1 - n_percent)
    filtered_df = df[df[column] >= threshold]
    return filtered_df
