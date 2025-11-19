import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

class DataStorage:
    """Handles persistent storage of analysis data and historical records."""
    
    def __init__(self, history_file: str = 'analysis_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load analysis history from JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_history(self):
        """Save analysis history to JSON file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=self._json_serializer)
        except IOError:
            pass  # Silently fail if unable to save
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for pandas objects."""
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict('index')
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        return str(obj)
    
    def save_analysis(self, filename: str, analysis_results: Dict[str, Any], total_rows: int):
        """Save analysis results to history."""
        # Convert pandas DataFrames to serializable format
        serializable_results = {}
        for key, value in analysis_results.items():
            if isinstance(value, pd.DataFrame):
                serializable_results[key] = value.to_dict('index')
            elif isinstance(value, pd.Series):
                serializable_results[key] = value.to_dict()
            else:
                serializable_results[key] = value
        
        # Create history record
        record = {
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'total_rows': total_rows,
            'analysis': serializable_results
        }
        
        # Add to history
        self.history.append(record)
        
        # Keep only last 50 records to prevent file from growing too large
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        # Save to file
        self._save_history()
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get all analysis history records."""
        return self.history.copy()
    
    def get_recent_analyses(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent n analysis records."""
        return self.history[-n:] if len(self.history) >= n else self.history.copy()
    
    def get_analysis_by_filename(self, filename: str) -> List[Dict[str, Any]]:
        """Get all analysis records for a specific filename."""
        return [record for record in self.history if record['filename'] == filename]
    
    def delete_analysis(self, timestamp: str) -> bool:
        """Delete an analysis record by timestamp."""
        original_length = len(self.history)
        self.history = [record for record in self.history if record['timestamp'] != timestamp]
        
        if len(self.history) < original_length:
            self._save_history()
            return True
        return False
    
    def clear_history(self):
        """Clear all analysis history."""
        self.history = []
        self._save_history()
    
    def get_history_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the analysis history."""
        if not self.history:
            return {
                'total_analyses': 0,
                'unique_files': 0,
                'date_range': None,
                'most_recent': None,
                'oldest': None
            }
        
        # Get unique filenames
        unique_files = set(record['filename'] for record in self.history)
        
        # Get date range
        timestamps = [record['timestamp'] for record in self.history]
        earliest = min(timestamps)
        latest = max(timestamps)
        
        summary = {
            'total_analyses': len(self.history),
            'unique_files': len(unique_files),
            'date_range': f"{earliest} to {latest}",
            'most_recent': latest,
            'oldest': earliest,
            'unique_filenames': list(unique_files)
        }
        
        return summary
    
    def export_history(self) -> str:
        """Export analysis history as JSON string."""
        return json.dumps(self.history, indent=2, default=self._json_serializer)
    
    def import_history(self, history_json: str) -> bool:
        """Import analysis history from JSON string."""
        try:
            imported_history = json.loads(history_json)
            if isinstance(imported_history, list):
                self.history = imported_history
                self._save_history()
                return True
        except json.JSONDecodeError:
            pass
        return False
