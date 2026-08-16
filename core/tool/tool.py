"""
Tool - Core tool definition and metadata
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from uuid import uuid4


class ToolStatus(Enum):
    """Tool execution status."""
    AVAILABLE = "available"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class ToolPermission(Enum):
    """Tool permission levels."""
    PUBLIC = "public"  # Available to all users
    AUTHENTICATED = "authenticated"  # Requires authentication
    AUTHORIZED = "authorized"  # Requires specific authorization
    ADMIN = "admin"  # Admin only


@dataclass
class ToolResult:
    """Result of tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolParameter:
    """Tool parameter definition."""
    name: str
    type: str
    required: bool = True
    default: Any = None
    description: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """
    Core tool definition with execution metadata.
    """
    tool_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    
    # Tool function
    function: Optional[Callable] = None
    parameters: List[ToolParameter] = field(default_factory=list)
    
    # Status and permissions
    status: ToolStatus = ToolStatus.AVAILABLE
    permission: ToolPermission = ToolPermission.AUTHENTICATED
    
    # Execution constraints
    timeout: Optional[int] = None  # seconds
    max_retries: int = 0
    retry_delay: int = 5  # seconds
    
    # Resource requirements
    required_resources: List[str] = field(default_factory=list)
    estimated_memory: int = 0  # MB
    estimated_cpu: float = 0.0  # percentage
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    
    # Usage statistics
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    
    def __post_init__(self):
        """Validate tool after initialization."""
        if not self.name:
            self.name = f"Tool_{self.tool_id[:8]}"
    
    def can_execute(self, user_permissions: List[str]) -> bool:
        """
        Check if tool can be executed by user with given permissions.
        
        Args:
            user_permissions: List of user permissions
            
        Returns:
            True if tool can be executed, False otherwise
        """
        if self.status != ToolStatus.AVAILABLE:
            return False
        
        if self.permission == ToolPermission.PUBLIC:
            return True
        elif self.permission == ToolPermission.AUTHENTICATED:
            return "authenticated" in user_permissions
        elif self.permission == ToolPermission.AUTHORIZED:
            return self.tool_id in user_permissions
        elif self.permission == ToolPermission.ADMIN:
            return "admin" in user_permissions
        
        return False
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate tool parameters.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in parameters:
                return False, f"Required parameter '{param.name}' is missing"
            
            # Check parameter type
            if param.name in parameters:
                value = parameters[param.name]
                if not self._validate_type(value, param.type):
                    return False, f"Parameter '{param.name}' must be of type {param.type}"
                
                # Check constraints
                if param.constraints:
                    is_valid, error = self._validate_constraints(value, param.constraints)
                    if not is_valid:
                        return False, f"Parameter '{param.name}' constraint error: {error}"
        
        return True, None
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate parameter type."""
        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, accept
    
    def _validate_constraints(self, value: Any, constraints: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate parameter constraints."""
        # Min/max for numeric values
        if "min" in constraints and value < constraints["min"]:
            return False, f"Value must be >= {constraints['min']}"
        if "max" in constraints and value > constraints["max"]:
            return False, f"Value must be <= {constraints['max']}"
        
        # Pattern for string values
        if "pattern" in constraints and isinstance(value, str):
            import re
            if not re.match(constraints["pattern"], value):
                return False, f"Value does not match pattern {constraints['pattern']}"
        
        # Enum values
        if "enum" in constraints and value not in constraints["enum"]:
            return False, f"Value must be one of {constraints['enum']}"
        
        return True, None
    
    def record_execution(self, result: ToolResult) -> None:
        """
        Record tool execution statistics.
        
        Args:
            result: Execution result
        """
        self.total_calls += 1
        self.last_used = datetime.now()
        
        if result.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
    
    def get_success_rate(self) -> float:
        """
        Get tool success rate.
        
        Returns:
            Success rate as percentage (0-100)
        """
        if self.total_calls == 0:
            return 0.0
        
        return (self.successful_calls / self.total_calls) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "status": self.status.value,
            "permission": self.permission.value,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "required_resources": self.required_resources,
            "estimated_memory": self.estimated_memory,
            "estimated_cpu": self.estimated_cpu,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "category": self.category,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": self.get_success_rate(),
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "required": p.required,
                    "default": p.default,
                    "description": p.description,
                    "constraints": p.constraints
                }
                for p in self.parameters
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tool':
        """Create tool from dictionary."""
        tool = cls(
            tool_id=data.get("tool_id", str(uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            status=ToolStatus(data.get("status", ToolStatus.AVAILABLE.value)),
            permission=ToolPermission(data.get("permission", ToolPermission.AUTHENTICATED.value)),
            timeout=data.get("timeout"),
            max_retries=data.get("max_retries", 0),
            retry_delay=data.get("retry_delay", 5),
            required_resources=data.get("required_resources", []),
            estimated_memory=data.get("estimated_memory", 0),
            estimated_cpu=data.get("estimated_cpu", 0.0),
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            category=data.get("category", "general"),
            metadata=data.get("metadata", {})
        )
        
        # Parse parameters
        if "parameters" in data:
            tool.parameters = [
                ToolParameter(
                    name=p["name"],
                    type=p["type"],
                    required=p.get("required", True),
                    default=p.get("default"),
                    description=p.get("description", ""),
                    constraints=p.get("constraints", {})
                )
                for p in data["parameters"]
            ]
        
        # Parse timestamps
        if data.get("created_at"):
            tool.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            tool.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("last_used"):
            tool.last_used = datetime.fromisoformat(data["last_used"])
        
        # Parse statistics
        tool.total_calls = data.get("total_calls", 0)
        tool.successful_calls = data.get("successful_calls", 0)
        tool.failed_calls = data.get("failed_calls", 0)
        
        return tool