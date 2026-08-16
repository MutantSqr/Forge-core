"""
Tool Registry - Dynamic tool registration and discovery
"""

import json
from typing import Dict, List, Optional, Callable
from pathlib import Path
from threading import Lock

from .tool import Tool, ToolStatus, ToolPermission, ToolParameter


class ToolRegistry:
    """
    Registry for managing tool registration and discovery.
    """
    
    def __init__(self, storage_path: str = "./tool_registry"):
        """
        Initialize the tool registry.
        
        Args:
            storage_path: Path to store tool definitions
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._tools: Dict[str, Tool] = {}
        self._lock = Lock()
        
        # Load existing tools
        self._load_tools()
    
    def register_tool(self, tool: Tool) -> bool:
        """
        Register a new tool.
        
        Args:
            tool: Tool to register
            
        Returns:
            Success status
        """
        with self._lock:
            if tool.tool_id in self._tools:
                return False  # Tool already registered
            
            self._tools[tool.tool_id] = tool
            self._save_tool(tool)
            
            return True
    
    def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_id: ID of tool to unregister
            
        Returns:
            Success status
        """
        with self._lock:
            if tool_id not in self._tools:
                return False
            
            del self._tools[tool_id]
            self._delete_tool(tool_id)
            
            return True
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """
        Get a tool by ID.
        
        Args:
            tool_id: ID of tool
            
        Returns:
            Tool or None if not found
        """
        with self._lock:
            return self._tools.get(tool_id)
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name: Name of tool
            
        Returns:
            Tool or None if not found
        """
        with self._lock:
            for tool in self._tools.values():
                if tool.name == name:
                    return tool
        return None
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """
        Get tools by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of tools in the category
        """
        with self._lock:
            return [tool for tool in self._tools.values() if tool.category == category]
    
    def get_tools_by_tag(self, tag: str) -> List[Tool]:
        """
        Get tools by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of tools with the tag
        """
        with self._lock:
            return [tool for tool in self._tools.values() if tag in tool.tags]
    
    def get_tools_by_permission(self, permission: ToolPermission) -> List[Tool]:
        """
        Get tools by permission level.
        
        Args:
            permission: Permission level to filter by
            
        Returns:
            List of tools with the permission level
        """
        with self._lock:
            return [tool for tool in self._tools.values() if tool.permission == permission]
    
    def get_available_tools(self, user_permissions: List[str]) -> List[Tool]:
        """
        Get tools available to a user with given permissions.
        
        Args:
            user_permissions: List of user permissions
            
        Returns:
            List of available tools
        """
        with self._lock:
            return [
                tool for tool in self._tools.values()
                if tool.can_execute(user_permissions)
            ]
    
    def list_tools(self) -> List[Tool]:
        """
        List all registered tools.
        
        Returns:
            List of all tools
        """
        with self._lock:
            return list(self._tools.values())
    
    def search_tools(self, query: str) -> List[Tool]:
        """
        Search tools by name, description, or tags.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        
        with self._lock:
            matching_tools = []
            for tool in self._tools.values():
                if (query_lower in tool.name.lower() or
                    query_lower in tool.description.lower() or
                    any(query_lower in tag.lower() for tag in tool.tags)):
                    matching_tools.append(tool)
            
            return matching_tools
    
    def update_tool(self, tool_id: str, updates: Dict[str, any]) -> bool:
        """
        Update a tool's metadata.
        
        Args:
            tool_id: ID of tool to update
            updates: Dictionary of fields to update
            
        Returns:
            Success status
        """
        with self._lock:
            if tool_id not in self._tools:
                return False
            
            tool = self._tools[tool_id]
            
            # Update allowed fields
            for field, value in updates.items():
                if hasattr(tool, field) and field not in ["tool_id", "created_at"]:
                    setattr(tool, field, value)
            
            tool.updated_at = datetime.now()
            self._save_tool(tool)
            
            return True
    
    def set_tool_status(self, tool_id: str, status: ToolStatus) -> bool:
        """
        Set the status of a tool.
        
        Args:
            tool_id: ID of tool
            status: New status
            
        Returns:
            Success status
        """
        return self.update_tool(tool_id, {"status": status})
    
    def get_tool_dependencies(self, tool_id: str) -> List[str]:
        """
        Get dependencies for a tool.
        
        Args:
            tool_id: ID of tool
            
        Returns:
            List of dependency tool IDs
        """
        tool = self.get_tool(tool_id)
        if tool:
            return tool.dependencies
        return []
    
    def check_dependencies(self, tool_id: str) -> tuple[bool, List[str]]:
        """
        Check if a tool's dependencies are satisfied.
        
        Args:
            tool_id: ID of tool
            
        Returns:
            Tuple of (all_satisfied, missing_dependencies)
        """
        tool = self.get_tool(tool_id)
        if not tool:
            return False, []
        
        missing = []
        for dep_id in tool.dependencies:
            dep_tool = self.get_tool(dep_id)
            if not dep_tool or dep_tool.status != ToolStatus.AVAILABLE:
                missing.append(dep_id)
        
        return len(missing) == 0, missing
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_tools = len(self._tools)
            
            status_counts = {}
            for tool in self._tools.values():
                status = tool.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            category_counts = {}
            for tool in self._tools.values():
                category = tool.category
                category_counts[category] = category_counts.get(category, 0) + 1
            
            permission_counts = {}
            for tool in self._tools.values():
                permission = tool.permission.value
                permission_counts[permission] = permission_counts.get(permission, 0) + 1
            
            return {
                "total_tools": total_tools,
                "status_breakdown": status_counts,
                "category_breakdown": category_counts,
                "permission_breakdown": permission_counts
            }
    
    def _load_tools(self) -> None:
        """Load tools from storage."""
        if not self.storage_path.exists():
            return
        
        for tool_file in self.storage_path.glob("*.json"):
            try:
                with open(tool_file, 'r') as f:
                    tool_data = json.load(f)
                    tool = Tool.from_dict(tool_data)
                    self._tools[tool.tool_id] = tool
            except Exception as e:
                print(f"Error loading tool from {tool_file}: {e}")
    
    def _save_tool(self, tool: Tool) -> None:
        """Save tool to storage."""
        tool_file = self.storage_path / f"{tool.tool_id}.json"
        try:
            with open(tool_file, 'w') as f:
                json.dump(tool.to_dict(), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving tool to {tool_file}: {e}")
    
    def _delete_tool(self, tool_id: str) -> None:
        """Delete tool from storage."""
        tool_file = self.storage_path / f"{tool_id}.json"
        try:
            if tool_file.exists():
                tool_file.unlink()
        except Exception as e:
            print(f"Error deleting tool file {tool_file}: {e}")
    
    def export_tools(self, export_path: str) -> bool:
        """
        Export all tools to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            Success status
        """
        try:
            export_data = {
                "tools": [tool.to_dict() for tool in self._tools.values()],
                "exported_at": datetime.now().isoformat()
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error exporting tools: {e}")
            return False
    
    def import_tools(self, import_path: str) -> int:
        """
        Import tools from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Number of tools imported
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for tool_data in import_data.get("tools", []):
                tool = Tool.from_dict(tool_data)
                if self.register_tool(tool):
                    imported_count += 1
            
            return imported_count
        except Exception as e:
            print(f"Error importing tools: {e}")
            return 0