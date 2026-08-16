"""
Module - Core module definition and metadata
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from uuid import uuid4


class ModuleStatus(Enum):
    """Module loading and execution status."""
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"
    UNLOADED = "unloaded"


class ModuleType(Enum):
    """Module types."""
    CORE = "core"  # Core system modules
    BUSINESS = "business"  # Business logic modules
    INTEGRATION = "integration"  # External integration modules
    UI = "ui"  # User interface modules
    ANALYTICS = "analytics"  # Analytics and reporting modules
    AI = "ai"  # AI/ML modules
    CUSTOM = "custom"  # Custom user modules


@dataclass
class ModuleDependency:
    """Module dependency definition."""
    module_id: str
    version: str = ">=1.0.0"
    optional: bool = False


@dataclass
class ModuleConfig:
    """Module configuration."""
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Module:
    """
    Core module definition with execution metadata.
    """
    module_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    
    # Module type and status
    module_type: ModuleType = ModuleType.CUSTOM
    status: ModuleStatus = ModuleStatus.UNLOADED
    
    # Module implementation
    initialize: Optional[Callable] = None
    execute: Optional[Callable] = None
    shutdown: Optional[Callable] = None
    
    # Dependencies
    dependencies: List[ModuleDependency] = field(default_factory=list)
    
    # Configuration
    config: ModuleConfig = field(default_factory=ModuleConfig)
    
    # Resources
    required_resources: List[str] = field(default_factory=list)
    provided_resources: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    loaded_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    
    # Usage statistics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    def __post_init__(self):
        """Validate module after initialization."""
        if not self.name:
            self.name = f"Module_{self.module_id[:8]}"
    
    def can_load(self, available_modules: Dict[str, 'Module']) -> tuple[bool, List[str]]:
        """
        Check if module can be loaded based on dependencies.
        
        Args:
            available_modules: Dictionary of available modules
            
        Returns:
            Tuple of (can_load, missing_dependencies)
        """
        missing = []
        
        for dep in self.dependencies:
            if dep.module_id not in available_modules:
                if not dep.optional:
                    missing.append(dep.module_id)
            else:
                # Check version compatibility (simplified)
                available_module = available_modules[dep.module_id]
                if not self._check_version_compatibility(dep.version, available_module.version):
                    if not dep.optional:
                        missing.append(f"{dep.module_id} (version mismatch)")
        
        return len(missing) == 0, missing
    
    def _check_version_compatibility(self, required_version: str, available_version: str) -> bool:
        """Check version compatibility (simplified)."""
        # In a real implementation, use proper version comparison
        return True
    
    def initialize_module(self) -> bool:
        """
        Initialize the module.
        
        Returns:
            Success status
        """
        if self.initialize:
            try:
                self.initialize(self.config.config)
                self.status = ModuleStatus.LOADED
                self.loaded_at = datetime.now()
                return True
            except Exception as e:
                self.status = ModuleStatus.ERROR
                print(f"Module initialization failed: {e}")
                return False
        else:
            self.status = ModuleStatus.LOADED
            self.loaded_at = datetime.now()
            return True
    
    def activate_module(self) -> bool:
        """
        Activate the module.
        
        Returns:
            Success status
        """
        if self.status != ModuleStatus.LOADED:
            return False
        
        self.status = ModuleStatus.ACTIVE
        self.activated_at = datetime.now()
        return True
    
    def deactivate_module(self) -> bool:
        """
        Deactivate the module.
        
        Returns:
            Success status
        """
        if self.status != ModuleStatus.ACTIVE:
            return False
        
        self.status = ModuleStatus.INACTIVE
        return True
    
    def execute_module(self, *args, **kwargs) -> Any:
        """
        Execute the module.
        
        Returns:
            Execution result
        """
        if self.status != ModuleStatus.ACTIVE:
            raise RuntimeError(f"Module {self.name} is not active")
        
        if not self.execute:
            raise RuntimeError(f"Module {self.name} has no execute function")
        
        try:
            result = self.execute(*args, **kwargs)
            self.total_executions += 1
            self.successful_executions += 1
            return result
        except Exception as e:
            self.total_executions += 1
            self.failed_executions += 1
            raise e
    
    def shutdown_module(self) -> bool:
        """
        Shutdown the module.
        
        Returns:
            Success status
        """
        if self.shutdown:
            try:
                self.shutdown()
            except Exception as e:
                print(f"Module shutdown failed: {e}")
        
        self.status = ModuleStatus.UNLOADED
        return True
    
    def get_success_rate(self) -> float:
        """
        Get module execution success rate.
        
        Returns:
            Success rate as percentage (0-100)
        """
        if self.total_executions == 0:
            return 0.0
        
        return (self.successful_executions / self.total_executions) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert module to dictionary."""
        return {
            "module_id": self.module_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "module_type": self.module_type.value,
            "status": self.status.value,
            "dependencies": [
                {
                    "module_id": dep.module_id,
                    "version": dep.version,
                    "optional": dep.optional
                }
                for dep in self.dependencies
            ],
            "config": {
                "enabled": self.config.enabled,
                "config": self.config.config,
                "permissions": self.config.permissions,
                "resources": self.config.resources
            },
            "required_resources": self.required_resources,
            "provided_resources": self.provided_resources,
            "tags": self.tags,
            "category": self.category,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.get_success_rate()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Module':
        """Create module from dictionary."""
        module = cls(
            module_id=data.get("module_id", str(uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            module_type=ModuleType(data.get("module_type", ModuleType.CUSTOM.value)),
            status=ModuleStatus(data.get("status", ModuleStatus.UNLOADED.value)),
            required_resources=data.get("required_resources", []),
            provided_resources=data.get("provided_resources", []),
            tags=data.get("tags", []),
            category=data.get("category", "general"),
            metadata=data.get("metadata", {})
        )
        
        # Parse dependencies
        if "dependencies" in data:
            module.dependencies = [
                ModuleDependency(
                    module_id=dep["module_id"],
                    version=dep.get("version", ">=1.0.0"),
                    optional=dep.get("optional", False)
                )
                for dep in data["dependencies"]
            ]
        
        # Parse config
        if "config" in data:
            config_data = data["config"]
            module.config = ModuleConfig(
                enabled=config_data.get("enabled", True),
                config=config_data.get("config", {}),
                permissions=config_data.get("permissions", []),
                resources=config_data.get("resources", {})
            )
        
        # Parse timestamps
        if data.get("created_at"):
            module.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            module.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("loaded_at"):
            module.loaded_at = datetime.fromisoformat(data["loaded_at"])
        if data.get("activated_at"):
            module.activated_at = datetime.fromisoformat(data["activated_at"])
        
        # Parse statistics
        module.total_executions = data.get("total_executions", 0)
        module.successful_executions = data.get("successful_executions", 0)
        module.failed_executions = data.get("failed_executions", 0)
        
        return module