"""
Module Manager - Orchestrate module loading, lifecycle, and dependencies
"""

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from .module import Module, ModuleStatus, ModuleType, ModuleDependency, ModuleConfig
from .module_registry import ModuleRegistry
from .module_loader import ModuleLoader
from .module_sandbox import ModuleSandbox


class ModuleManager:
    """
    Main module manager that coordinates module registration, loading, and lifecycle management.
    """
    
    def __init__(self, 
                 storage_path: str = "./module_registry",
                 enable_sandbox: bool = True):
        """
        Initialize the module manager.
        
        Args:
            storage_path: Path to store module definitions
            enable_sandbox: Whether to enable sandboxed execution
        """
        self.registry = ModuleRegistry(storage_path=storage_path)
        self.loader = ModuleLoader()
        self.sandbox = ModuleSandbox() if enable_sandbox else None
        
        self._active_modules: Dict[str, Module] = {}
        
    def create_module(self,
                     name: str,
                     module_type: ModuleType = ModuleType.CUSTOM,
                     initialize_func: Optional[Callable] = None,
                     execute_func: Optional[Callable] = None,
                     shutdown_func: Optional[Callable] = None,
                     dependencies: Optional[List[ModuleDependency]] = None,
                     config: Optional[ModuleConfig] = None,
                     category: str = "general",
                     tags: Optional[List[str]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Module:
        """
        Create a new module.
        
        Args:
            name: Module name
            module_type: Module type
            initialize_func: Initialization function
            execute_func: Execution function
            shutdown_func: Shutdown function
            dependencies: Module dependencies
            config: Module configuration
            category: Module category
            tags: Module tags
            metadata: Additional metadata
            
        Returns:
            Created module
        """
        module = Module(
            name=name,
            module_type=module_type,
            initialize=initialize_func,
            execute=execute_func,
            shutdown=shutdown_func,
            dependencies=dependencies or [],
            config=config or ModuleConfig(),
            category=category,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.registry.register_module(module)
        return module
    
    def load_module(self, module_id: str, use_sandbox: bool = False) -> bool:
        """
        Load and initialize a module.
        
        Args:
            module_id: ID of module to load
            use_sandbox: Whether to use sandbox for execution
            
        Returns:
            Success status
        """
        module = self.registry.get_module(module_id)
        if not module:
            return False
        
        # Check dependencies
        deps_satisfied, missing_deps = self.registry.check_dependencies(module_id)
        if not deps_satisfied:
            print(f"Cannot load module {module.name}: missing dependencies {missing_deps}")
            return False
        
        # Initialize module
        if not module.initialize_module():
            return False
        
        # Activate module
        if not module.activate_module():
            return False
        
        self._active_modules[module_id] = module
        return True
    
    def unload_module(self, module_id: str) -> bool:
        """
        Unload and shutdown a module.
        
        Args:
            module_id: ID of module to unload
            
        Returns:
            Success status
        """
        module = self._active_modules.get(module_id)
        if not module:
            return False
        
        # Deactivate module
        module.deactivate_module()
        
        # Shutdown module
        module.shutdown_module()
        
        # Remove from active modules
        del self._active_modules[module_id]
        
        return True
    
    def execute_module(self, module_id: str, *args, **kwargs) -> Any:
        """
        Execute a module.
        
        Args:
            module_id: ID of module to execute
            args: Positional arguments for module execution
            kwargs: Keyword arguments for module execution
            
        Returns:
            Module execution result
        """
        module = self._active_modules.get(module_id)
        if not module:
            raise RuntimeError(f"Module {module_id} is not active")
        
        if self.sandbox:
            # Execute in sandbox
            result = self.sandbox.execute_module_function(
                module.execute_module,
                *args,
                **kwargs
            )
            
            if result["success"]:
                return result["result"]
            else:
                raise RuntimeError(f"Module execution failed: {result['error']}")
        else:
            # Execute normally
            return module.execute_module(*args, **kwargs)
    
    def get_module(self, module_id: str) -> Optional[Module]:
        """
        Get a module by ID.
        
        Args:
            module_id: ID of module
            
        Returns:
            Module or None if not found
        """
        return self.registry.get_module(module_id)
    
    def get_active_modules(self) -> List[Module]:
        """
        Get all active modules.
        
        Returns:
            List of active modules
        """
        return list(self._active_modules.values())
    
    def get_modules_by_type(self, module_type: ModuleType) -> List[Module]:
        """
        Get modules by type.
        
        Args:
            module_type: Module type
            
        Returns:
            List of modules of the specified type
        """
        return self.registry.get_modules_by_type(module_type)
    
    def load_from_file(self, file_path: str, module_name: Optional[str] = None) -> Optional[Module]:
        """
        Load a module from a file.
        
        Args:
            file_path: Path to module file
            module_name: Optional module name
            
        Returns:
            Loaded module or None if failed
        """
        return self.loader.load_from_file(file_path, module_name)
    
    def load_from_directory(self, directory: str) -> List[Module]:
        """
        Load all modules from a directory.
        
        Args:
            directory: Path to directory
            
        Returns:
            List of loaded modules
        """
        return self.loader.load_from_directory(directory)
    
    def get_load_order(self) -> List[str]:
        """
        Get the recommended load order for modules.
        
        Returns:
            List of module IDs in load order
        """
        return self.registry.get_load_order()
    
    def load_all_modules(self) -> Dict[str, bool]:
        """
        Load all modules in dependency order.
        
        Returns:
            Dictionary mapping module IDs to load success status
        """
        load_order = self.get_load_order()
        results = {}
        
        for module_id in load_order:
            results[module_id] = self.load_module(module_id)
        
        return results
    
    def update_module_config(self, module_id: str, config: ModuleConfig) -> bool:
        """
        Update module configuration.
        
        Args:
            module_id: ID of module
            config: New configuration
            
        Returns:
            Success status
        """
        return self.registry.update_module(module_id, {"config": config})
    
    def enable_module(self, module_id: str) -> bool:
        """
        Enable a module.
        
        Args:
            module_id: ID of module
            
        Returns:
            Success status
        """
        module = self.registry.get_module(module_id)
        if module:
            module.config.enabled = True
            return self.registry.update_module(module_id, {"config": module.config})
        return False
    
    def disable_module(self, module_id: str) -> bool:
        """
        Disable a module.
        
        Args:
            module_id: ID of module
            
        Returns:
            Success status
        """
        module = self.registry.get_module(module_id)
        if module:
            module.config.enabled = False
            if module_id in self._active_modules:
                self.unload_module(module_id)
            return self.registry.update_module(module_id, {"config": module.config})
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get module manager statistics.
        
        Returns:
            Dictionary with statistics
        """
        registry_stats = self.registry.get_statistics()
        
        active_count = len(self._active_modules)
        
        # Calculate success rates
        success_rates = {}
        for module in self._active_modules.values():
            if module.total_executions > 0:
                success_rates[module.module_id] = module.get_success_rate()
        
        return {
            "registry": registry_stats,
            "active_modules": active_count,
            "success_rates": success_rates,
            "sandbox_enabled": self.sandbox is not None
        }
    
    def create_module_group(self, 
                           module_ids: List[str],
                           group_name: str,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a group of related modules.
        
        Args:
            module_ids: List of module IDs to group
            group_name: Name for the module group
            metadata: Additional metadata
            
        Returns:
            Group ID
        """
        group_id = f"group_{group_name}_{datetime.now().isoformat()}"
        
        for module_id in module_ids:
            module = self.registry.get_module(module_id)
            if module:
                module.metadata["group_id"] = group_id
                module.metadata["group_name"] = group_name
                if metadata:
                    module.metadata.update(metadata)
        
        return group_id
    
    def get_group_modules(self, group_id: str) -> List[Module]:
        """
        Get all modules in a group.
        
        Args:
            group_id: Group ID
            
        Returns:
            List of modules in the group
        """
        modules = []
        for module in self.registry.list_modules():
            if module.metadata.get("group_id") == group_id:
                modules.append(module)
        return modules
    
    def export_modules(self, export_path: str) -> bool:
        """
        Export all modules to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            Success status
        """
        return self.registry.export_modules(export_path)
    
    def import_modules(self, import_path: str) -> int:
        """
        Import modules from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Number of modules imported
        """
        return self.registry.import_modules(import_path)
    
    def shutdown(self) -> None:
        """Shutdown the module manager."""
        # Unload all active modules
        for module_id in list(self._active_modules.keys()):
            self.unload_module(module_id)
        
        # Cleanup sandbox
        if self.sandbox:
            self.sandbox.cleanup()