"""
Module Registry - Dynamic module registration and discovery
"""

import json
import importlib.util
import sys
from typing import Dict, List, Optional, Callable
from pathlib import Path
from threading import Lock

from .module import Module, ModuleStatus, ModuleType, ModuleDependency


class ModuleRegistry:
    """
    Registry for managing module registration and discovery.
    """
    
    def __init__(self, storage_path: str = "./module_registry"):
        """
        Initialize the module registry.
        
        Args:
            storage_path: Path to store module definitions
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._modules: Dict[str, Module] = {}
        self._lock = Lock()
        
        # Load existing modules
        self._load_modules()
    
    def register_module(self, module: Module) -> bool:
        """
        Register a new module.
        
        Args:
            module: Module to register
            
        Returns:
            Success status
        """
        with self._lock:
            if module.module_id in self._modules:
                return False  # Module already registered
            
            self._modules[module.module_id] = module
            self._save_module(module)
            
            return True
    
    def unregister_module(self, module_id: str) -> bool:
        """
        Unregister a module.
        
        Args:
            module_id: ID of module to unregister
            
        Returns:
            Success status
        """
        with self._lock:
            if module_id not in self._modules:
                return False
            
            # Shutdown module if active
            module = self._modules[module_id]
            if module.status == ModuleStatus.ACTIVE:
                module.shutdown_module()
            
            del self._modules[module_id]
            self._delete_module(module_id)
            
            return True
    
    def get_module(self, module_id: str) -> Optional[Module]:
        """
        Get a module by ID.
        
        Args:
            module_id: ID of module
            
        Returns:
            Module or None if not found
        """
        with self._lock:
            return self._modules.get(module_id)
    
    def get_module_by_name(self, name: str) -> Optional[Module]:
        """
        Get a module by name.
        
        Args:
            name: Name of module
            
        Returns:
            Module or None if not found
        """
        with self._lock:
            for module in self._modules.values():
                if module.name == name:
                    return module
        return None
    
    def get_modules_by_type(self, module_type: ModuleType) -> List[Module]:
        """
        Get modules by type.
        
        Args:
            module_type: Module type to filter by
            
        Returns:
            List of modules of the specified type
        """
        with self._lock:
            return [module for module in self._modules.values() if module.module_type == module_type]
    
    def get_modules_by_status(self, status: ModuleStatus) -> List[Module]:
        """
        Get modules by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of modules with the specified status
        """
        with self._lock:
            return [module for module in self._modules.values() if module.status == status]
    
    def get_modules_by_category(self, category: str) -> List[Module]:
        """
        Get modules by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of modules in the category
        """
        with self._lock:
            return [module for module in self._modules.values() if module.category == category]
    
    def get_modules_by_tag(self, tag: str) -> List[Module]:
        """
        Get modules by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of modules with the tag
        """
        with self._lock:
            return [module for module in self._modules.values() if tag in module.tags]
    
    def list_modules(self) -> List[Module]:
        """
        List all registered modules.
        
        Returns:
            List of all modules
        """
        with self._lock:
            return list(self._modules.values())
    
    def search_modules(self, query: str) -> List[Module]:
        """
        Search modules by name, description, or tags.
        
        Args:
            query: Search query
            
        Returns:
            List of matching modules
        """
        query_lower = query.lower()
        
        with self._lock:
            matching_modules = []
            for module in self._modules.values():
                if (query_lower in module.name.lower() or
                    query_lower in module.description.lower() or
                    any(query_lower in tag.lower() for tag in module.tags)):
                    matching_modules.append(module)
            
            return matching_modules
    
    def update_module(self, module_id: str, updates: Dict[str, any]) -> bool:
        """
        Update a module's metadata.
        
        Args:
            module_id: ID of module to update
            updates: Dictionary of fields to update
            
        Returns:
            Success status
        """
        with self._lock:
            if module_id not in self._modules:
                return False
            
            module = self._modules[module_id]
            
            # Update allowed fields
            for field, value in updates.items():
                if hasattr(module, field) and field not in ["module_id", "created_at"]:
                    setattr(module, field, value)
            
            module.updated_at = datetime.now()
            self._save_module(module)
            
            return True
    
    def set_module_status(self, module_id: str, status: ModuleStatus) -> bool:
        """
        Set the status of a module.
        
        Args:
            module_id: ID of module
            status: New status
            
        Returns:
            Success status
        """
        return self.update_module(module_id, {"status": status})
    
    def get_module_dependencies(self, module_id: str) -> List[ModuleDependency]:
        """
        Get dependencies for a module.
        
        Args:
            module_id: ID of module
            
        Returns:
            List of dependency definitions
        """
        module = self.get_module(module_id)
        if module:
            return module.dependencies
        return []
    
    def check_dependencies(self, module_id: str) -> tuple[bool, List[str]]:
        """
        Check if a module's dependencies are satisfied.
        
        Args:
            module_id: ID of module
            
        Returns:
            Tuple of (all_satisfied, missing_dependencies)
        """
        module = self.get_module(module_id)
        if not module:
            return False, []
        
        with self._lock:
            available_modules = self._modules
        
        can_load, missing = module.can_load(available_modules)
        return can_load, missing
    
    def get_load_order(self) -> List[str]:
        """
        Get the recommended load order for modules based on dependencies.
        
        Returns:
            List of module IDs in load order
        """
        # Simple topological sort based on dependencies
        load_order = []
        loaded_modules = set()
        
        remaining_modules = list(self._modules.values())
        
        while remaining_modules:
            # Find modules with all dependencies satisfied
            ready_modules = []
            for module in remaining_modules:
                can_load, _ = module.can_load(
                    {m.module_id: m for m in self._modules.values() if m.module_id in loaded_modules}
                )
                if can_load:
                    ready_modules.append(module)
            
            if not ready_modules:
                # Circular dependency or missing dependency
                # Add remaining modules in any order
                load_order.extend(m.module_id for m in remaining_modules)
                break
            
            for module in ready_modules:
                load_order.append(module.module_id)
                loaded_modules.add(module.module_id)
                remaining_modules.remove(module)
        
        return load_order
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_modules = len(self._modules)
            
            status_counts = {}
            for module in self._modules.values():
                status = module.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            type_counts = {}
            for module in self._modules.values():
                mtype = module.module_type.value
                type_counts[mtype] = type_counts.get(mtype, 0) + 1
            
            category_counts = {}
            for module in self._modules.values():
                category = module.category
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                "total_modules": total_modules,
                "status_breakdown": status_counts,
                "type_breakdown": type_counts,
                "category_breakdown": category_counts
            }
    
    def _load_modules(self) -> None:
        """Load modules from storage."""
        if not self.storage_path.exists():
            return
        
        for module_file in self.storage_path.glob("*.json"):
            try:
                with open(module_file, 'r') as f:
                    module_data = json.load(f)
                    module = Module.from_dict(module_data)
                    self._modules[module.module_id] = module
            except Exception as e:
                print(f"Error loading module from {module_file}: {e}")
    
    def _save_module(self, module: Module) -> None:
        """Save module to storage."""
        module_file = self.storage_path / f"{module.module_id}.json"
        try:
            with open(module_file, 'w') as f:
                json.dump(module.to_dict(), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving module to {module_file}: {e}")
    
    def _delete_module(self, module_id: str) -> None:
        """Delete module from storage."""
        module_file = self.storage_path / f"{module_id}.json"
        try:
            if module_file.exists():
                module_file.unlink()
        except Exception as e:
            print(f"Error deleting module file {module_file}: {e}")
    
    def export_modules(self, export_path: str) -> bool:
        """
        Export all modules to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            Success status
        """
        try:
            export_data = {
                "modules": [module.to_dict() for module in self._modules.values()],
                "exported_at": datetime.now().isoformat()
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error exporting modules: {e}")
            return False
    
    def import_modules(self, import_path: str) -> int:
        """
        Import modules from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Number of modules imported
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for module_data in import_data.get("modules", []):
                module = Module.from_dict(module_data)
                if self.register_module(module):
                    imported_count += 1
            
            return imported_count
        except Exception as e:
            print(f"Error importing modules: {e}")
            return 0