"""
Security Audit Logger - Log security events for compliance and monitoring
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock


class SecurityAuditLogger:
    """
    Logger for security-related events and actions.
    """
    
    def __init__(self, log_path: str = "./security_audit.log"):
        """
        Initialize the security audit logger.
        
        Args:
            log_path: Path to the audit log file
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._in_memory_logs: List[Dict[str, Any]] = []
        self._lock = Lock()
        
    def log_security_event(self,
                          event_type: str,
                          username: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None,
                          severity: str = "info") -> bool:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            username: Username associated with the event
            details: Additional event details
            severity: Event severity (info, warning, error, critical)
            
        Returns:
            Success status
        """
        timestamp = datetime.now()
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "username": username,
            "details": details or {},
            "severity": severity
        }
        
        with self._lock:
            self._in_memory_logs.append(log_entry)
            
            # Keep in-memory logs manageable
            if len(self._in_memory_logs) > 1000:
                self._in_memory_logs = self._in_memory_logs[-500:]
        
        # Write to file
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            return True
        except Exception as e:
            print(f"Error writing to audit log: {e}")
            return False
    
    def get_logs(self,
                start_date: Optional[datetime] = None,
                end_date: Optional[datetime] = None,
                event_type: Optional[str] = None,
                username: Optional[str] = None,
                severity: Optional[str] = None,
                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get filtered log entries.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            event_type: Event type filter
            username: Username filter
            severity: Severity filter
            limit: Maximum number of entries to return
            
        Returns:
            List of matching log entries
        """
        with self._lock:
            filtered_logs = self._in_memory_logs.copy()
        
        # Apply filters
        if start_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log["timestamp"]) <= end_date
            ]
        
        if event_type:
            filtered_logs = [
                log for log in filtered_logs
                if log["event_type"] == event_type
            ]
        
        if username:
            filtered_logs = [
                log for log in filtered_logs
                if log["username"] == username
            ]
        
        if severity:
            filtered_logs = [
                log for log in filtered_logs
                if log["severity"] == severity
            ]
        
        # Sort by timestamp (newest first) and limit
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered_logs[:limit]
    
    def get_logs_by_user(self, username: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get logs for a specific user.
        
        Args:
            username: Username
            limit: Maximum number of entries
            
        Returns:
            List of log entries for the user
        """
        return self.get_logs(username=username, limit=limit)
    
    def get_logs_by_event_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get logs for a specific event type.
        
        Args:
            event_type: Event type
            limit: Maximum number of entries
            
        Returns:
            List of log entries for the event type
        """
        return self.get_logs(event_type=event_type, limit=limit)
    
    def get_critical_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get critical security events.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of critical log entries
        """
        return self.get_logs(severity="critical", limit=limit)
    
    def get_failed_authentications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get failed authentication attempts.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of failed authentication logs
        """
        failed_auth_logs = []
        
        with self._lock:
            for log in self._in_memory_logs:
                if (log["event_type"] == "user_authentication" and
                    not log["details"].get("success", False)):
                    failed_auth_logs.append(log)
        
        failed_auth_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return failed_auth_logs[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get audit log statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_logs = len(self._in_memory_logs)
            
            if total_logs == 0:
                return {
                    "total_logs": 0,
                    "event_types": {},
                    "severity_breakdown": {},
                    "unique_users": 0
                }
        
        # Count by event type
        event_types = {}
        for log in self._in_memory_logs:
            event_type = log["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Count by severity
        severity_breakdown = {}
        for log in self._in_memory_logs:
            severity = log["severity"]
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        
        # Count unique users
        unique_users = set()
        for log in self._in_memory_logs:
            if log["username"]:
                unique_users.add(log["username"])
        
        return {
            "total_logs": total_logs,
            "event_types": event_types,
            "severity_breakdown": severity_breakdown,
            "unique_users": len(unique_users)
        }
    
    def export_logs(self, export_path: str, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> bool:
        """
        Export logs to a file.
        
        Args:
            export_path: Path to export file
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Success status
        """
        logs = self.get_logs(start_date=start_date, end_date=end_date, limit=10000)
        
        try:
            with open(export_path, 'w') as f:
                json.dump(logs, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
    
    def clear_old_logs(self, days_to_keep: int = 30) -> int:
        """
        Clear logs older than specified days.
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            Number of logs cleared
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self._lock:
            original_count = len(self._in_memory_logs)
            self._in_memory_logs = [
                log for log in self._in_memory_logs
                if datetime.fromisoformat(log["timestamp"]) >= cutoff_date
            ]
            cleared = original_count - len(self._in_memory_logs)
        
        return cleared
    
    def generate_security_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security report.
        
        Returns:
            Dictionary with security report data
        """
        stats = self.get_stats()
        failed_auth = self.get_failed_authentications(limit=100)
        critical_events = self.get_critical_events(limit=50)
        
        return {
            "report_generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "recent_failed_authentications": failed_auth[:10],
            "recent_critical_events": critical_events[:10],
            "security_recommendations": self._generate_recommendations(stats, failed_auth, critical_events)
        }
    
    def _generate_recommendations(self, stats: Dict, failed_auth: List, critical_events: List) -> List[str]:
        """Generate security recommendations based on log analysis."""
        recommendations = []
        
        # Check for high failed authentication rate
        if len(failed_auth) > 10:
            recommendations.append("High number of failed authentication attempts detected - consider implementing rate limiting")
        
        # Check for critical events
        if len(critical_events) > 0:
            recommendations.append(f"{len(critical_events)} critical security events detected - immediate review recommended")
        
        # Check for unusual patterns
        if stats.get("severity_breakdown", {}).get("error", 0) > 10:
            recommendations.append("High number of error-level security events - review system configuration")
        
        if not recommendations:
            recommendations.append("No immediate security concerns detected")
        
        return recommendations