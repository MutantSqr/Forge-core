"""
Task - Core task definition and status management
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from uuid import uuid4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class TaskResult:
    """Result of task execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """
    Core task definition with execution metadata.
    """
    task_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    
    # Task execution details
    action: Optional[Callable] = None
    action_args: Dict[str, Any] = field(default_factory=dict)
    action_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Execution constraints
    timeout: Optional[int] = None  # seconds
    max_retries: int = 0
    retry_count: int = 0
    retry_delay: int = 5  # seconds
    
    # Resources
    required_resources: List[str] = field(default_factory=list)
    allocated_resources: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    result: Optional[TaskResult] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate task after initialization."""
        if not self.name:
            self.name = f"Task_{self.task_id[:8]}"
    
    def can_execute(self) -> bool:
        """Check if task can be executed."""
        return (
            self.status == TaskStatus.QUEUED and
            (self.scheduled_at is None or self.scheduled_at <= datetime.now()) and
            self.retry_count <= self.max_retries
        )
    
    def should_retry(self) -> bool:
        """Check if task should be retried."""
        return (
            self.status == TaskStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def mark_started(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_completed(self, result: TaskResult) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
    
    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.result = TaskResult(success=False, error=error)
    
    def mark_cancelled(self) -> None:
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def increment_retry(self) -> None:
        """Increment retry count and mark for retry."""
        self.retry_count += 1
        self.status = TaskStatus.RETRYING
    
    def get_execution_time(self) -> Optional[float]:
        """Get task execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def is_expired(self) -> bool:
        """Check if task has exceeded its timeout."""
        if self.timeout and self.started_at:
            elapsed = (datetime.now() - self.started_at).total_seconds()
            return elapsed > self.timeout
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "required_resources": self.required_resources,
            "allocated_resources": self.allocated_resources,
            "result": {
                "success": self.result.success,
                "data": self.result.data,
                "error": self.result.error,
                "execution_time": self.result.execution_time
            } if self.result else None,
            "metadata": self.metadata,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            task_id=data.get("task_id", str(uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            dependencies=data.get("dependencies", []),
            dependents=data.get("dependents", []),
            timeout=data.get("timeout"),
            max_retries=data.get("max_retries", 0),
            retry_count=data.get("retry_count", 0),
            retry_delay=data.get("retry_delay", 5),
            required_resources=data.get("required_resources", []),
            allocated_resources=data.get("allocated_resources", {}),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", [])
        )
        
        # Parse datetime fields
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("scheduled_at"):
            task.scheduled_at = datetime.fromisoformat(data["scheduled_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        # Parse result
        if data.get("result"):
            result_data = data["result"]
            task.result = TaskResult(
                success=result_data.get("success", False),
                data=result_data.get("data"),
                error=result_data.get("error"),
                execution_time=result_data.get("execution_time", 0.0)
            )
        
        return task