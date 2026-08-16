"""
Tool Executor - Execute tools with timeout and error handling
"""

import threading
import time
import traceback
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime

from .tool import Tool, ToolStatus, ToolResult


class ToolExecutor:
    """
    Tool executor with timeout handling, retry logic, and parallel execution.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the tool executor.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running_executions: Dict[str, Future] = {}
        self._lock = threading.Lock()
        self._execution_callbacks: List[Callable] = []
        
    def execute(self, tool: Tool, parameters: Dict[str, Any], 
                user_permissions: List[str]) -> ToolResult:
        """
        Execute a tool with given parameters.
        
        Args:
            tool: Tool to execute
            parameters: Tool parameters
            user_permissions: User permissions
            
        Returns:
            Tool execution result
        """
        # Check permissions
        if not tool.can_execute(user_permissions):
            return ToolResult(
                success=False,
                error="Permission denied"
            )
        
        # Check tool status
        if tool.status != ToolStatus.AVAILABLE:
            return ToolResult(
                success=False,
                error=f"Tool is not available (status: {tool.status.value})"
            )
        
        # Validate parameters
        is_valid, error = tool.validate_parameters(parameters)
        if not is_valid:
            return ToolResult(
                success=False,
                error=f"Parameter validation failed: {error}"
            )
        
        # Execute the tool
        start_time = time.time()
        
        try:
            if tool.function:
                # Execute with timeout
                result_data = self._execute_with_timeout(
                    tool.function, 
                    parameters, 
                    tool.timeout
                )
                
                result = ToolResult(
                    success=True,
                    data=result_data,
                    execution_time=time.time() - start_time
                )
                
                tool.record_execution(result)
                self._notify_callbacks(tool, parameters, result)
                
                return result
            else:
                return ToolResult(
                    success=False,
                    error="Tool has no executable function",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            result = ToolResult(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time
            )
            
            tool.record_execution(result)
            self._notify_callbacks(tool, parameters, result)
            
            return result
    
    def execute_async(self, tool: Tool, parameters: Dict[str, Any],
                     user_permissions: List[str], callback: Optional[Callable] = None) -> bool:
        """
        Execute a tool asynchronously.
        
        Args:
            tool: Tool to execute
            parameters: Tool parameters
            user_permissions: User permissions
            callback: Optional callback for completion
            
        Returns:
            Success status
        """
        def execution_wrapper():
            result = self.execute(tool, parameters, user_permissions)
            if callback:
                callback(tool, parameters, result)
        
        try:
            future = self._executor.submit(execution_wrapper)
            return True
        except Exception as e:
            print(f"Error submitting async execution: {e}")
            return False
    
    def _execute_with_timeout(self, func: Callable, parameters: Dict[str, Any], 
                            timeout: Optional[int]) -> Any:
        """
        Execute a function with timeout.
        
        Args:
            func: Function to execute
            parameters: Function parameters
            timeout: Timeout in seconds
            
        Returns:
            Function result
            
        Raises:
            TimeoutError: If execution exceeds timeout
        """
        if timeout is None:
            return func(**parameters)
        
        result_container = [None]
        exception_container = [None]
        
        def execution_thread():
            try:
                result_container[0] = func(**parameters)
            except Exception as e:
                exception_container[0] = e
        
        thread = threading.Thread(target=execution_thread)
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Tool execution exceeded timeout of {timeout} seconds")
        
        if exception_container[0]:
            raise exception_container[0]
        
        return result_container[0]
    
    def add_execution_callback(self, callback: Callable) -> None:
        """
        Add a callback to be called on tool execution completion.
        
        Args:
            callback: Callback function that takes (tool, parameters, result)
        """
        self._execution_callbacks.append(callback)
    
    def _notify_callbacks(self, tool: Tool, parameters: Dict[str, Any], 
                         result: ToolResult) -> None:
        """Notify all registered callbacks of tool execution."""
        for callback in self._execution_callbacks:
            try:
                callback(tool, parameters, result)
            except Exception as e:
                print(f"Error in execution callback: {e}")
    
    def get_execution_stats(self) -> Dict[str, any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary with execution statistics
        """
        with self._lock:
            return {
                "max_workers": self.max_workers,
                "running_executions": len(self._running_executions),
                "available_workers": self.max_workers - len(self._running_executions)
            }
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.
        
        Args:
            wait: Whether to wait for running executions to complete
        """
        self._executor.shutdown(wait=wait)
        
        with self._lock:
            self._running_executions.clear()
    
    def execute_batch(self, tools: List[tuple[Tool, Dict[str, Any], List[str]]]) -> List[ToolResult]:
        """
        Execute multiple tools in batch.
        
        Args:
            tools: List of (tool, parameters, user_permissions) tuples
            
        Returns:
            List of execution results
        """
        results = []
        
        for tool, parameters, permissions in tools:
            result = self.execute(tool, parameters, permissions)
            results.append(result)
        
        return results
    
    def execute_parallel(self, tools: List[tuple[Tool, Dict[str, Any], List[str]]]) -> List[ToolResult]:
        """
        Execute multiple tools in parallel.
        
        Args:
            tools: List of (tool, parameters, user_permissions) tuples
            
        Returns:
            List of execution results
        """
        def execute_wrapper(tool, parameters, permissions):
            return self.execute(tool, parameters, permissions)
        
        futures = []
        for tool, parameters, permissions in tools:
            future = self._executor.submit(execute_wrapper, tool, parameters, permissions)
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(ToolResult(
                    success=False,
                    error=str(e)
                ))
        
        return results