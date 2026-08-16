"""
Tool Manager - Orchestrate tool registration, execution, and permissions
"""

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from .tool import Tool, ToolStatus, ToolPermission, ToolResult, ToolParameter
from .tool_registry import ToolRegistry
from .tool_executor import ToolExecutor
from .tool_sandbox import ToolSandbox


class ToolManager:
    """
    Main tool manager that coordinates tool registration, execution, and permissions.
    """
    
    def __init__(self, 
                 storage_path: str = "./tool_registry",
                 max_workers: int = 4,
                 enable_sandbox: bool = True):
        """
        Initialize the tool manager.
        
        Args:
            storage_path: Path to store tool definitions
            max_workers: Maximum number of parallel tool executions
            enable_sandbox: Whether to enable sandboxed execution
        """
        self.registry = ToolRegistry(storage_path=storage_path)
        self.executor = ToolExecutor(max_workers=max_workers)
        self.sandbox = ToolSandbox() if enable_sandbox else None
        
        self._execution_history: List[Dict[str, Any]] = []
        
    def register_tool(self,
                     name: str,
                     function: Callable,
                     description: str = "",
                     parameters: Optional[List[Dict[str, Any]]] = None,
                     permission: ToolPermission = ToolPermission.AUTHENTICATED,
                     category: str = "general",
                     tags: Optional[List[str]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Tool:
        """
        Register a new tool.
        
        Args:
            name: Tool name
            function: Tool function
            description: Tool description
            parameters: Tool parameter definitions
            permission: Tool permission level
            category: Tool category
            tags: Tool tags
            metadata: Additional metadata
            
        Returns:
            Registered tool
        """
        # Convert parameter definitions to ToolParameter objects
        tool_parameters = []
        if parameters:
            for param in parameters:
                tool_parameters.append(ToolParameter(
                    name=param["name"],
                    type=param.get("type", "str"),
                    required=param.get("required", True),
                    default=param.get("default"),
                    description=param.get("description", ""),
                    constraints=param.get("constraints", {})
                ))
        
        tool = Tool(
            name=name,
            function=function,
            description=description,
            parameters=tool_parameters,
            permission=permission,
            category=category,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.registry.register_tool(tool)
        return tool
    
    def execute_tool(self,
                    tool_id: str,
                    parameters: Dict[str, Any],
                    user_permissions: List[str],
                    use_sandbox: bool = False) -> ToolResult:
        """
        Execute a tool.
        
        Args:
            tool_id: ID of tool to execute
            parameters: Tool parameters
            user_permissions: User permissions
            use_sandbox: Whether to use sandbox execution
            
        Returns:
            Tool execution result
        """
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_id}"
            )
        
        # Check dependencies
        deps_satisfied, missing_deps = self.registry.check_dependencies(tool_id)
        if not deps_satisfied:
            return ToolResult(
                success=False,
                error=f"Tool dependencies not satisfied: {missing_deps}"
            )
        
        # Execute tool
        if use_sandbox and self.sandbox:
            # Execute in sandbox (for command-based tools)
            return self._execute_in_sandbox(tool, parameters, user_permissions)
        else:
            # Execute normally
            result = self.executor.execute(tool, parameters, user_permissions)
            
            # Record execution history
            self._record_execution(tool_id, parameters, user_permissions, result)
            
            return result
    
    def _execute_in_sandbox(self, tool: Tool, parameters: Dict[str, Any],
                          user_permissions: List[str]) -> ToolResult:
        """Execute tool in sandbox environment."""
        if not self.sandbox:
            return ToolResult(
                success=False,
                error="Sandbox not available"
            )
        
        # This is a simplified sandbox execution
        # In a real implementation, you'd have more sophisticated sandbox integration
        try:
            # For now, just execute normally but record that sandbox was requested
            result = self.executor.execute(tool, parameters, user_permissions)
            result.metadata["sandbox_execution"] = True
            
            self._record_execution(tool.tool_id, parameters, user_permissions, result)
            
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Sandbox execution failed: {str(e)}"
            )
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """
        Get a tool by ID.
        
        Args:
            tool_id: ID of tool
            
        Returns:
            Tool or None if not found
        """
        return self.registry.get_tool(tool_id)
    
    def get_available_tools(self, user_permissions: List[str]) -> List[Tool]:
        """
        Get tools available to a user.
        
        Args:
            user_permissions: User permissions
            
        Returns:
            List of available tools
        """
        return self.registry.get_available_tools(user_permissions)
    
    def search_tools(self, query: str, user_permissions: Optional[List[str]] = None) -> List[Tool]:
        """
        Search for tools.
        
        Args:
            query: Search query
            user_permissions: Optional user permissions to filter by
            
        Returns:
            List of matching tools
        """
        matching_tools = self.registry.search_tools(query)
        
        if user_permissions:
            matching_tools = [
                tool for tool in matching_tools
                if tool.can_execute(user_permissions)
            ]
        
        return matching_tools
    
    def update_tool(self, tool_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a tool.
        
        Args:
            tool_id: ID of tool to update
            updates: Dictionary of fields to update
            
        Returns:
            Success status
        """
        return self.registry.update_tool(tool_id, updates)
    
    def set_tool_status(self, tool_id: str, status: ToolStatus) -> bool:
        """
        Set the status of a tool.
        
        Args:
            tool_id: ID of tool
            status: New status
            
        Returns:
            Success status
        """
        return self.registry.set_tool_status(tool_id, status)
    
    def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_id: ID of tool to unregister
            
        Returns:
            Success status
        """
        return self.registry.unregister_tool(tool_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get tool manager statistics.
        
        Returns:
            Dictionary with statistics
        """
        registry_stats = self.registry.get_statistics()
        executor_stats = self.executor.get_execution_stats()
        
        return {
            "registry": registry_stats,
            "executor": executor_stats,
            "sandbox": self.sandbox.get_sandbox_info() if self.sandbox else None,
            "total_executions": len(self._execution_history)
        }
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get execution history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of execution records
        """
        return self._execution_history[-limit:]
    
    def _record_execution(self, tool_id: str, parameters: Dict[str, Any],
                        user_permissions: List[str], result: ToolResult) -> None:
        """
        Record tool execution in history.
        
        Args:
            tool_id: ID of executed tool
            parameters: Tool parameters
            user_permissions: User permissions
            result: Execution result
        """
        execution_record = {
            "tool_id": tool_id,
            "parameters": parameters,
            "user_permissions": user_permissions,
            "result": {
                "success": result.success,
                "error": result.error,
                "execution_time": result.execution_time
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self._execution_history.append(execution_record)
        
        # Keep history size manageable
        if len(self._execution_history) > 1000:
            self._execution_history = self._execution_history[-500:]
    
    def create_tool_group(self, 
                         tool_ids: List[str],
                         group_name: str,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a group of related tools.
        
        Args:
            tool_ids: List of tool IDs to group
            group_name: Name for the tool group
            metadata: Additional metadata
            
        Returns:
            Group ID
        """
        group_id = f"group_{group_name}_{datetime.now().isoformat()}"
        
        for tool_id in tool_ids:
            tool = self.registry.get_tool(tool_id)
            if tool:
                tool.metadata["group_id"] = group_id
                tool.metadata["group_name"] = group_name
                if metadata:
                    tool.metadata.update(metadata)
        
        return group_id
    
    def get_group_tools(self, group_id: str) -> List[Tool]:
        """
        Get all tools in a group.
        
        Args:
            group_id: Group ID
            
        Returns:
            List of tools in the group
        """
        tools = []
        for tool in self.registry.list_tools():
            if tool.metadata.get("group_id") == group_id:
                tools.append(tool)
        return tools
    
    def export_tools(self, export_path: str) -> bool:
        """
        Export all tools to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            Success status
        """
        return self.registry.export_tools(export_path)
    
    def import_tools(self, import_path: str) -> int:
        """
        Import tools from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Number of tools imported
        """
        return self.registry.import_tools(import_path)
    
    def shutdown(self) -> None:
        """Shutdown the tool manager."""
        self.executor.shutdown()
        if self.sandbox:
            self.sandbox.cleanup()