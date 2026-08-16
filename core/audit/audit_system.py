"""
Audit System - Main orchestration of audit components
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .event_logger import EventLogger
from .performance_monitor import PerformanceMonitor
from .error_tracker import ErrorTracker
from .compliance_reporter import ComplianceReporter


class AuditSystem:
    """
    Main audit system that coordinates event logging, performance monitoring, 
    error tracking, and compliance reporting.
    """
    
    def __init__(self, 
                 log_path: str = "./audit_logs",
                 enable_performance_monitoring: bool = True,
                 enable_error_tracking: bool = True,
                 enable_compliance_reporting: bool = True):
        """
        Initialize the audit system.
        
        Args:
            log_path: Path to store audit logs
            enable_performance_monitoring: Whether to enable performance monitoring
            enable_error_tracking: Whether to enable error tracking
            enable_compliance_reporting: Whether to enable compliance reporting
        """
        self.event_logger = EventLogger(log_path=log_path)
        self.performance_monitor = PerformanceMonitor(log_path=log_path) if enable_performance_monitoring else None
        self.error_tracker = ErrorTracker(log_path=log_path) if enable_error_tracking else None
        self.compliance_reporter = ComplianceReporter(log_path=log_path) if enable_compliance_reporting else None
        
        self._enable_performance_monitoring = enable_performance_monitoring
        self._enable_error_tracking = enable_error_tracking
        self._enable_compliance_reporting = enable_compliance_reporting
    
    def log_event(self,
                 event_type: str,
                 source: str,
                 details: Optional[Dict[str, Any]] = None,
                 severity: str = "info",
                 user_id: Optional[str] = None) -> bool:
        """
        Log an event.
        
        Args:
            event_type: Type of event
            source: Source of the event
            details: Additional event details
            severity: Event severity
            user_id: User ID associated with the event
            
        Returns:
            Success status
        """
        return self.event_logger.log_event(
            event_type=event_type,
            source=source,
            details=details,
            severity=severity,
            user_id=user_id
        )
    
    def start_performance_metric(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start tracking a performance metric.
        
        Args:
            operation_name: Name of the operation
            metadata: Additional metadata
            
        Returns:
            Metric ID
        """
        if not self._enable_performance_monitoring or not self.performance_monitor:
            return ""
        
        return self.performance_monitor.start_metric(operation_name, metadata)
    
    def end_performance_metric(self, metric_id: str, success: bool = True) -> Optional[Dict[str, Any]]:
        """
        End tracking a performance metric.
        
        Args:
            metric_id: Metric ID
            success: Whether the operation was successful
            
        Returns:
            Performance metric data
        """
        if not self._enable_performance_monitoring or not self.performance_monitor:
            return None
        
        return self.performance_monitor.end_metric(metric_id, success)
    
    def track_error(self,
                   error_type: str,
                   error_message: str,
                   stack_trace: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None,
                   user_id: Optional[str] = None) -> bool:
        """
        Track an error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace
            context: Additional context
            user_id: User ID associated with the error
            
        Returns:
            Success status
        """
        if not self._enable_error_tracking or not self.error_tracker:
            return False
        
        return self.error_tracker.track_error(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context,
            user_id=user_id
        )
    
    def generate_compliance_report(self, 
                                  report_type: str = "general",
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a compliance report.
        
        Args:
            report_type: Type of compliance report
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            Compliance report data
        """
        if not self._enable_compliance_reporting or not self.compliance_reporter:
            return {"error": "Compliance reporting not enabled"}
        
        return self.compliance_reporter.generate_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_audit_trail(self,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       event_type: Optional[str] = None,
                       user_id: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit trail entries.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            event_type: Event type filter
            user_id: User ID filter
            limit: Maximum number of entries
            
        Returns:
            List of audit trail entries
        """
        return self.event_logger.get_events(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            user_id=user_id,
            limit=limit
        )
    
    def get_performance_metrics(self,
                               operation_name: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get performance metrics.
        
        Args:
            operation_name: Operation name filter
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of entries
            
        Returns:
            List of performance metrics
        """
        if not self._enable_performance_monitoring or not self.performance_monitor:
            return []
        
        return self.performance_monitor.get_metrics(
            operation_name=operation_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def get_errors(self,
                  error_type: Optional[str] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get tracked errors.
        
        Args:
            error_type: Error type filter
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of entries
            
        Returns:
            List of error entries
        """
        if not self._enable_error_tracking or not self.error_tracker:
            return []
        
        return self.error_tracker.get_errors(
            error_type=error_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            Dictionary with system health information
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "event_logging": "healthy",
            "performance_monitoring": "disabled" if not self._enable_performance_monitoring else "healthy",
            "error_tracking": "disabled" if not self._enable_error_tracking else "healthy",
            "compliance_reporting": "disabled" if not self._enable_compliance_reporting else "healthy"
        }
        
        # Get component statistics
        event_stats = self.event_logger.get_statistics()
        health["event_statistics"] = event_stats
        
        if self._enable_performance_monitoring and self.performance_monitor:
            perf_stats = self.performance_monitor.get_statistics()
            health["performance_statistics"] = perf_stats
        
        if self._enable_error_tracking and self.error_tracker:
            error_stats = self.error_tracker.get_statistics()
            health["error_statistics"] = error_stats
        
        return health
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive audit report.
        
        Returns:
            Dictionary with comprehensive audit data
        """
        report = {
            "report_generated_at": datetime.now().isoformat(),
            "system_health": self.get_system_health(),
            "recent_events": self.get_audit_trail(limit=50),
            "performance_summary": self.get_performance_metrics(limit=50) if self._enable_performance_monitoring else [],
            "recent_errors": self.get_errors(limit=50) if self._enable_error_tracking else [],
            "compliance_status": self.generate_compliance_report() if self._enable_compliance_reporting else {}
        }
        
        return report
    
    def export_audit_data(self, export_path: str, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> bool:
        """
        Export audit data to a file.
        
        Args:
            export_path: Path to export file
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Success status
        """
        audit_data = {
            "exported_at": datetime.now().isoformat(),
            "events": self.get_audit_trail(start_date=start_date, end_date=end_date, limit=10000),
            "performance_metrics": self.get_performance_metrics(start_date=start_date, end_date=end_date, limit=10000) if self._enable_performance_monitoring else [],
            "errors": self.get_errors(start_date=start_date, end_date=end_date, limit=10000) if self._enable_error_tracking else []
        }
        
        try:
            import json
            with open(export_path, 'w') as f:
                json.dump(audit_data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting audit data: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """
        Clean up old audit data.
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            "events_cleaned": self.event_logger.cleanup_old_events(days_to_keep)
        }
        
        if self._enable_performance_monitoring and self.performance_monitor:
            stats["performance_metrics_cleaned"] = self.performance_monitor.cleanup_old_metrics(days_to_keep)
        
        if self._enable_error_tracking and self.error_tracker:
            stats["errors_cleaned"] = self.error_tracker.cleanup_old_errors(days_to_keep)
        
        return stats