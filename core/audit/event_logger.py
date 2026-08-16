"""
Event Logger - Comprehensive event logging for audit trails
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from threading import Lock
from enum import Enum


class EventSeverity(Enum):
    """Event severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventLogger:
    """
    Logger for tracking system events for audit trails.
    """
    
    def __init__(self, log_path: str = "./audit_logs"):
        """
        Initialize the event logger.
        
        Args:
            log_path: Path to store event logs
        """
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self._in_memory_events: List[Dict[str, Any]] = []
        self._lock = Lock()
        
    def log_event(self,
                 event_type: str,
                 source: str,
                 details: Optional[Dict[str, Any]] = None,
                 severity: str = "info",
                 user_id: Optional[str] = None,
                 session_id: Optional[str] = None) -> bool:
        """
        Log an event.
        
        Args:
            event_type: Type of event
            source: Source of the event
            details: Additional event details
            severity: Event severity
            user_id: User ID associated with the event
            session_id: Session ID
            
        Returns:
            Success status
        """
        timestamp = datetime.now()
        
        event = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "source": source,
            "details": details or {},
            "severity": severity,
            "user_id": user_id,
            "session_id": session_id,
            "event_id": self._generate_event_id()
        }
        
        with self._lock:
            self._in_memory_events.append(event)
            
            # Keep in-memory events manageable
            if len(self._in_memory_events) > 10000:
                self._in_memory_events = self._in_memory_events[-5000:]
        
        # Write to file
        try:
            log_file = self.log_path / f"events_{timestamp.strftime('%Y%m%d')}.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(event, default=self._json_serializer) + '\n')
            return True
        except Exception as e:
            print(f"Error writing event log: {e}")
            return False
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _json_serializer(self, obj):
        """
        Custom JSON serializer for non-serializable objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serializable representation of the object
        """
        # Handle dataclasses
        if hasattr(obj, '__dataclass_fields__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        
        # Handle objects with to_dict method
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # Handle enums
        if isinstance(obj, Enum):
            return obj.value
        
        # Handle other non-serializable objects by converting to string
        return str(obj)
    
    def get_events(self,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  event_type: Optional[str] = None,
                  source: Optional[str] = None,
                  severity: Optional[str] = None,
                  user_id: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get filtered events.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            event_type: Event type filter
            source: Source filter
            severity: Severity filter
            user_id: User ID filter
            limit: Maximum number of entries
            
        Returns:
            List of matching events
        """
        with self._lock:
            filtered_events = self._in_memory_events.copy()
        
        # Apply filters
        if start_date:
            filtered_events = [
                event for event in filtered_events
                if datetime.fromisoformat(event["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_events = [
                event for event in filtered_events
                if datetime.fromisoformat(event["timestamp"]) <= end_date
            ]
        
        if event_type:
            filtered_events = [
                event for event in filtered_events
                if event["event_type"] == event_type
            ]
        
        if source:
            filtered_events = [
                event for event in filtered_events
                if event["source"] == source
            ]
        
        if severity:
            filtered_events = [
                event for event in filtered_events
                if event["severity"] == severity
            ]
        
        if user_id:
            filtered_events = [
                event for event in filtered_events
                if event["user_id"] == user_id
            ]
        
        # Sort by timestamp (newest first) and limit
        filtered_events.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered_events[:limit]
    
    def get_events_by_user(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get events for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of entries
            
        Returns:
            List of events for the user
        """
        return self.get_events(user_id=user_id, limit=limit)
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get events for a specific type.
        
        Args:
            event_type: Event type
            limit: Maximum number of entries
            
        Returns:
            List of events of the specified type
        """
        return self.get_events(event_type=event_type, limit=limit)
    
    def get_critical_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get critical events.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of critical events
        """
        return self.get_events(severity="critical", limit=limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get event logger statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_events = len(self._in_memory_events)
            
            if total_events == 0:
                return {
                    "total_events": 0,
                    "event_types": {},
                    "severity_breakdown": {},
                    "sources": {},
                    "unique_users": 0
                }
        
        # Count by event type
        event_types = {}
        for event in self._in_memory_events:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Count by severity
        severity_breakdown = {}
        for event in self._in_memory_events:
            severity = event["severity"]
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        
        # Count by source
        sources = {}
        for event in self._in_memory_events:
            source = event["source"]
            sources[source] = sources.get(source, 0) + 1
        
        # Count unique users
        unique_users = set()
        for event in self._in_memory_events:
            if event["user_id"]:
                unique_users.add(event["user_id"])
        
        return {
            "total_events": total_events,
            "event_types": event_types,
            "severity_breakdown": severity_breakdown,
            "sources": sources,
            "unique_users": len(unique_users)
        }
    
    def cleanup_old_events(self, days_to_keep: int = 30) -> int:
        """
        Clean up events older than specified days.
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            Number of events cleaned
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self._lock:
            original_count = len(self._in_memory_events)
            self._in_memory_events = [
                event for event in self._in_memory_events
                if datetime.fromisoformat(event["timestamp"]) >= cutoff_date
            ]
            cleared = original_count - len(self._in_memory_events)
        
        # Clean up old log files
        try:
            cutoff_date_str = cutoff_date.strftime('%Y%m%d')
            for log_file in self.log_path.glob("events_*.log"):
                file_date_str = log_file.stem.split('_')[1]
                if file_date_str < cutoff_date_str:
                    log_file.unlink()
        except Exception as e:
            print(f"Error cleaning up old log files: {e}")
        
        return cleared
    
    def export_events(self, export_path: str,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> bool:
        """
        Export events to a file.
        
        Args:
            export_path: Path to export file
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Success status
        """
        events = self.get_events(start_date=start_date, end_date=end_date, limit=10000)
        
        try:
            with open(export_path, 'w') as f:
                json.dump(events, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting events: {e}")
            return False