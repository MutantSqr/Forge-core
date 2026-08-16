"""
Performance Monitor - Track system performance metrics
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from time import time


class PerformanceMonitor:
    """
    Monitor for tracking system performance metrics.
    """
    
    def __init__(self, log_path: str = "./audit_logs"):
        """
        Initialize the performance monitor.
        
        Args:
            log_path: Path to store performance logs
        """
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self._active_metrics: Dict[str, Dict[str, Any]] = {}
        self._completed_metrics: List[Dict[str, Any]] = []
        self._lock = Lock()
        
    def start_metric(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start tracking a performance metric.
        
        Args:
            operation_name: Name of the operation
            metadata: Additional metadata
            
        Returns:
            Metric ID
        """
        metric_id = self._generate_metric_id()
        start_time = time()
        
        metric = {
            "metric_id": metric_id,
            "operation_name": operation_name,
            "start_time": start_time,
            "start_timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "status": "active"
        }
        
        with self._lock:
            self._active_metrics[metric_id] = metric
        
        return metric_id
    
    def end_metric(self, metric_id: str, success: bool = True, result: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """
        End tracking a performance metric.
        
        Args:
            metric_id: Metric ID
            success: Whether the operation was successful
            result: Operation result
            
        Returns:
            Completed metric data
        """
        with self._lock:
            if metric_id not in self._active_metrics:
                return None
            
            metric = self._active_metrics[metric_id]
            end_time = time()
            
            completed_metric = {
                "metric_id": metric_id,
                "operation_name": metric["operation_name"],
                "start_time": metric["start_time"],
                "end_time": end_time,
                "duration": end_time - metric["start_time"],
                "start_timestamp": metric["start_timestamp"],
                "end_timestamp": datetime.now().isoformat(),
                "success": success,
                "result": str(result) if result else None,
                "metadata": metric["metadata"],
                "status": "completed"
            }
            
            # Move to completed metrics
            self._completed_metrics.append(completed_metric)
            del self._active_metrics[metric_id]
            
            # Keep completed metrics manageable
            if len(self._completed_metrics) > 10000:
                self._completed_metrics = self._completed_metrics[-5000:]
        
        # Write to file
        self._write_metric_to_file(completed_metric)
        
        return completed_metric
    
    def _generate_metric_id(self) -> str:
        """Generate a unique metric ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _write_metric_to_file(self, metric: Dict[str, Any]) -> None:
        """Write metric to file."""
        try:
            log_file = self.log_path / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(metric) + '\n')
        except Exception as e:
            print(f"Error writing performance log: {e}")
    
    def get_metrics(self,
                   operation_name: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get filtered performance metrics.
        
        Args:
            operation_name: Operation name filter
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of entries
            
        Returns:
            List of matching metrics
        """
        with self._lock:
            filtered_metrics = self._completed_metrics.copy()
        
        # Apply filters
        if operation_name:
            filtered_metrics = [
                metric for metric in filtered_metrics
                if metric["operation_name"] == operation_name
            ]
        
        if start_date:
            filtered_metrics = [
                metric for metric in filtered_metrics
                if datetime.fromisoformat(metric["start_timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_metrics = [
                metric for metric in filtered_metrics
                if datetime.fromisoformat(metric["end_timestamp"]) <= end_date
            ]
        
        # Sort by start timestamp (newest first) and limit
        filtered_metrics.sort(key=lambda x: x["start_timestamp"], reverse=True)
        return filtered_metrics[:limit]
    
    def get_active_metrics(self) -> List[Dict[str, Any]]:
        """
        Get currently active metrics.
        
        Returns:
            List of active metrics
        """
        with self._lock:
            return list(self._active_metrics.values())
    
    def get_operation_statistics(self, operation_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific operation.
        
        Args:
            operation_name: Operation name
            
        Returns:
            Dictionary with operation statistics
        """
        metrics = self.get_metrics(operation_name=operation_name, limit=10000)
        
        if not metrics:
            return {
                "operation_name": operation_name,
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_duration": 0.0,
                "min_duration": 0.0,
                "max_duration": 0.0
            }
        
        durations = [metric["duration"] for metric in metrics]
        successful = sum(1 for metric in metrics if metric["success"])
        failed = len(metrics) - successful
        
        return {
            "operation_name": operation_name,
            "total_executions": len(metrics),
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": (successful / len(metrics)) * 100,
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "median_duration": sorted(durations)[len(durations) // 2]
        }
    
    def get_slow_operations(self, threshold_seconds: float = 1.0, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get slow operations.
        
        Args:
            threshold_seconds: Duration threshold
            limit: Maximum number of entries
            
        Returns:
            List of slow operations
        """
        slow_ops = [
            metric for metric in self._completed_metrics
            if metric["duration"] > threshold_seconds
        ]
        
        slow_ops.sort(key=lambda x: x["duration"], reverse=True)
        return slow_ops[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get performance monitor statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_metrics = len(self._completed_metrics)
            active_count = len(self._active_metrics)
        
        if total_metrics == 0:
            return {
                "total_metrics": 0,
                "active_metrics": active_count,
                "operations": {},
                "average_duration": 0.0
            }
        
        # Count by operation
        operations = {}
        total_duration = 0.0
        
        for metric in self._completed_metrics:
            op_name = metric["operation_name"]
            operations[op_name] = operations.get(op_name, 0) + 1
            total_duration += metric["duration"]
        
        return {
            "total_metrics": total_metrics,
            "active_metrics": active_count,
            "operations": operations,
            "average_duration": total_duration / total_metrics
        }
    
    def cleanup_old_metrics(self, days_to_keep: int = 30) -> int:
        """
        Clean up metrics older than specified days.
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            Number of metrics cleaned
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self._lock:
            original_count = len(self._completed_metrics)
            self._completed_metrics = [
                metric for metric in self._completed_metrics
                if datetime.fromisoformat(metric["start_timestamp"]) >= cutoff_date
            ]
            cleared = original_count - len(self._completed_metrics)
        
        # Clean up old log files
        try:
            cutoff_date_str = cutoff_date.strftime('%Y%m%d')
            for log_file in self.log_path.glob("performance_*.log"):
                file_date_str = log_file.stem.split('_')[1]
                if file_date_str < cutoff_date_str:
                    log_file.unlink()
        except Exception as e:
            print(f"Error cleaning up old performance log files: {e}")
        
        return cleared
    
    def export_metrics(self, export_path: str,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> bool:
        """
        Export metrics to a file.
        
        Args:
            export_path: Path to export file
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Success status
        """
        metrics = self.get_metrics(start_date=start_date, end_date=end_date, limit=10000)
        
        try:
            with open(export_path, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting metrics: {e}")
            return False