"""
Module Loader - Dynamic module loading from various sources
"""

import importlib.util
import sys
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from .module import Module, ModuleStatus, ModuleType


class ModuleLoader:
    """
    Dynamic module loader for loading modules from various sources.
    """
    
    def __init__(self):
        """Initialize the module loader."""
        self._loaded_modules: Dict[str, Any] = {}
        
    def load_from_file(self, file_path: str, module_name: Optional[str] = None) -> Optional[Module]:
        """
        Load a module from a Python file.
        
        Args:
            file_path: Path to the Python file
            module_name: Optional module name
            
        Returns:
            Loaded module or None if failed
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Module file not found: {file_path}")
            
            module_name = module_name or file_path.stem
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module from {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._loaded_modules[module_name] = module
            
            # Create Module object if the file follows the expected pattern
            if hasattr(module, 'create_module'):
                return module.create_module()
            
            return None
            
        except Exception as e:
            print(f"Error loading module from file: {e}")
            return None
    
    def load_from_directory(self, directory: str) -> List[Module]:
        """
        Load all modules from a directory.
        
        Args:
            directory: Path to directory containing modules
            
        Returns:
            List of loaded modules
        """
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            return []
        
        loaded_modules = []
        
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # Skip private files
            
            module = self.load_from_file(str(file_path))
            if module:
                loaded_modules.append(module)
        
        return loaded_modules
    
    def load_from_package(self, package_name: str) -> Optional[Module]:
        """
        Load a module from an installed package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Loaded module or None if failed
        """
        try:
            module = importlib.import_module(package_name)
            self._loaded_modules[package_name] = module
            
            # Create Module object if the package follows the expected pattern
            if hasattr(module, 'create_module'):
                return module.create_module()
            
            return None
            
        except ImportError as e:
            print(f"Error importing package {package_name}: {e}")
            return None
    
    def unload_module(self, module_name: str) -> bool:
        """
        Unload a module.
        
        Args:
            module_name: Name of module to unload
            
        Returns:
            Success status
        """
        if module_name in self._loaded_modules:
            del self._loaded_modules[module_name]
            if module_name in sys.modules:
                del sys.modules[module_name]
            return True
        return False
    
    def reload_module(self, module_name: str) -> Optional[Any]:
        """
        Reload a module.
        
        Args:
            module_name: Name of module to reload
            
        Returns:
            Reloaded module or None if failed
        """
        if module_name not in self._loaded_modules:
            return None
        
        try:
            module = self._loaded_modules[module_name]
            reloaded_module = importlib.reload(module)
            self._loaded_modules[module_name] = reloaded_module
            return reloaded_module
        except Exception as e:
            print(f"Error reloading module {module_name}: {e}")
            return None
    
    def get_loaded_module(self, module_name: str) -> Optional[Any]:
        """
        Get a loaded module by name.
        
        Args:
            module_name: Name of module
            
        Returns:
            Loaded module or None if not found
        """
        return self._loaded_modules.get(module_name)
    
    def list_loaded_modules(self) -> List[str]:
        """
        List all loaded module names.
        
        Returns:
            List of module names
        """
        return list(self._loaded_modules.keys())
    
    def create_module_from_functions(self,
                                    name: str,
                                    initialize_func: Optional[callable] = None,
                                    execute_func: Optional[callable] = None,
                                    shutdown_func: Optional[callable] = None,
                                    **kwargs) -> Module:
        """
        Create a module from functions.
        
        Args:
            name: Module name
            initialize_func: Initialization function
            execute_func: Execution function
            shutdown_func: Shutdown function
            **kwargs: Additional module parameters
            
        Returns:
            Created module
        """
        module = Module(
            name=name,
            initialize=initialize_func,
            execute=execute_func,
            shutdown=shutdown_func,
            **kwargs
        )
        
        return module
    
    def validate_module(self, module: Module) -> tuple[bool, List[str]]:
        """
        Validate a module structure.
        
        Args:
            module: Module to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not module.name:
            errors.append("Module name is required")
        
        if not module.version:
            errors.append("Module version is required")
        
        if module.execute is None:
            errors.append("Module must have an execute function")
        
        # Check dependencies
        for dep in module.dependencies:
            if not dep.module_id:
                errors.append(f"Dependency missing module_id: {dep}")
        
        return len(errors) == 0, errors
    
    def get_module_info(self, module: Any) -> Dict[str, Any]:
        """
        Get information about a loaded module.
        
        Args:
            module: Loaded module
            
        Returns:
            Dictionary with module information
        """
        info = {
            "name": getattr(module, '__name__', 'unknown'),
            "file": getattr(module, '__file__', 'unknown'),
            "doc": getattr(module, '__doc__', ''),
            "attributes": []
        }
        
        # Get public attributes
        for attr_name in dir(module):
            if not attr_name.startswith('_'):
                attr = getattr(module, attr_name)
                if callable(attr):
                    info["attributes"].append({
                        "name": attr_name,
                        "type": "function",
                        "doc": getattr(attr, '__doc__', '')
                    })
                else:
                    info["attributes"].append({
                        "name": attr_name,
                        "type": type(attr).__name__,
                        "value": str(attr) if len(str(attr)) < 100 else f"{str(attr)[:100]}..."
                    })
        
        return info