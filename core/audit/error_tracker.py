"""
Error Tracker - Track and analyze system errors
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorTracker:
    """
    Tracker for monitoring and analyzing system errors.
    """
    
    def __init__(self, log_path: str = "./audit_logs"):
        """
        Initialize the error tracker.
        
        Args:
            log_path: Path to store error logs
        """
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self._errors: List[Dict[str, Any]] = []
        self._error_patterns: Dict[str, int] = {}
        self._lock = Lock()
        
    def track_error(self,
                   error_type: str,
                   error_message: str,
                   stack_trace: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None,
                   severity: str = "medium",
                   user_id: Optional[str] = None,
                   session_id: Optional[str] = None) -> bool:
        """
        Track an error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace
            context: Additional context
            severity: Error severity
            user_id: User ID associated with the error
            session_id: Session ID
            
        Returns:
            Success status
        """
        timestamp = datetime.now()
        error_id = self._generate_error_id()
        
        error = {
            "error_id": error_id,
            "timestamp": timestamp.isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context or {},
            "severity": severity,
            "user_id": user_id,
            "session_id": session_id,
            "resolved": False,
            "resolution_notes": None
        }
        
        with self._lock:
            self._errors.append(error)
            
            # Track error patterns
            pattern_key = f"{error_type}:{error_message[:100]}"
            self._error_patterns[pattern_key] = self._error_patterns.get(pattern_key, 0) + 1
            
            # Keep errors manageable
            if len(self._errors) > 10000:
                self._errors = self._errors[-5000]
        
        # Write to file
        self._write_error_to_file(error)
        
        return True
    
    def _generate_error_id(self) -> str:
        """Generate a unique error ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _write_error_to_file(self, error: Dict[str, Any]) -> None:
        """Write error to file."""
        try:
            log_file = self.log_path / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(error) + '\n')
        except Exception as e:
            print(f"Error writing error log: {e}")
    
    def get_errors(self,
                  error_type: Optional[str] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  severity: Optional[str] = None,
                  user_id: Optional[str] = None,
                  resolved: Optional[bool] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get filtered errors.
        
        Args:
            error_type: Error type filter
            start_date: Start date filter
            end_date: End date filter
            severity: Severity filter
            user_id: User ID filter
            resolved: Resolved status filter
            limit: Maximum number of entries
            
        Returns:
            List of matching errors
        """
        with self._lock:
            filtered_errors = self._errors.copy()
        
        # Apply filters
        if error_type:
            filtered_errors = [
                error for error in filtered_errors
                if error["error_type"] == error_type
            ]
        
        if start_date:
            filtered_errors = [
                error for error in filtered_errors
                if datetime.fromisoformat(error["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_errors = [
                error for error in filtered_errors
                if datetime.fromisoformat(error["timestamp"]) <= end_date
            ]
        
        if severity:
            filtered_errors = [
                error for error in filtered_errors
                if error["severity"] == severity
            ]
        
        if user_id:
            filtered_errors = [
                error for error in filtered_errors
                if error["user_id"] == user_id
            ]
        
        if resolved is not None:
            filtered_errors = [
                error for error in filtered_errors
                if error["resolved"] == resolved
            ]
        
        # Sort by timestamp (newest first) and limit
        filtered_errors.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered_errors[:limit]
    
    def resolve_error(self, error_id: str, resolution_notes: str) -> bool:
        """
        Mark an error as resolved.
        
        Args:
            error_id: Error ID
            resolution_notes: Notes about the resolution
            
        Returns:
            Success status
        """
        with self._lock:
            for error in self._errors:
                if error["error_id"] == error_id:
                    error["resolved"] = True
                    error["resolution_notes"] = resolution_notes
                    error["resolved_at"] = datetime.now().isoformat()
                    return True
        return False
    
    def get_error_patterns(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get common error patterns.
        
        Args:
            limit: Maximum number of patterns
            
        Returns:
            List of error patterns with occurrence counts
        """
        with self._lock:
            sorted_patterns = sorted(
                self._error_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )
        
        return [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted_patterns[:limit]
        ]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error tracker statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_errors = len(self._errors)
            
            if total_errors == 0:
                return {
                    "total_errors": 0,
                    "error_types": {},
                    "severity_breakdown": {},
                    "resolved_errors": 0,
                    "unresolved_errors": 0
                }
        
        # Count by error type
        error_types = {}
        for error in self._errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Count by severity
        severity_breakdown = {}
        for error in self._errors:
            severity = error["severity"]
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        
        # Count resolved vs unresolved
        resolved = sum(1 for error in self._errors if error["resolved"])
        unresolved = total_errors - resolved
        
        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "severity_breakdown": severity_breakdown,
            "resolved_errors": resolved,
            "unresolved_errors": unresolved,
            "resolution_rate": (resolved / total_errors) * 100 if total_errors > 0 else 0
        }
    
    def get_critical_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get critical errors.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of critical errors
        """
        return self.get_errors(severity="critical", resolved=False, limit=limit)
    
    def get_recent_errors(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent errors.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of entries
            
        Returns:
            List of recent errors
        """
        start_date = datetime.now() - timedelta(hours=hours)
        return self.get_errors(start_date=start_date, limit=limit)
    
    def cleanup_old_errors(self, days_to_keep: int = 30) -> int:
        """
        Clean up errors older than specified days.
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            Number of errors cleaned
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self._lock:
            original_count = len(self._errors)
            self._errors = [
                error for error in self._errors
                if datetime.fromisoformat(error["timestamp"]) >= cutoff_date
            ]
            cleared = original_count - len(self._errors)
        
        # Clean up old log files
        try:
            cutoff_date_str = cutoff_date.strftime('%Y%m%d')
            for log_file in self.log_path.glob("errors_*.log"):
                file_date_str = log_file.stem.split('_')[1]
                if file_date_str < cutoff_date_str:
                    log_file.unlink()
        except Exception as e:
            print(f"Error cleaning up old error log files: {e}")
        
        return cleared
    
    def export_errors(self, export_path: str,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> bool:
        """
        Export errors to a file.
        
        Args:
            export_path: Path to export file
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Success status
        """
        errors = self.get_errors(start_date=start_date, end_date=end_date, limit=10000)
        
        try:
            with open(export_path, 'w') as f:
                json.dump(errors, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting errors: {e}")
            return False