"""
Task Executor - Execute tasks with timeout and retry handling
"""

import threading
import time
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime

from .task import Task, TaskStatus, TaskResult


class TaskExecutor:
    """
    Task executor with timeout handling, retry logic, and parallel execution.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the task executor.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running_tasks: Dict[str, Future] = {}
        self._lock = threading.Lock()
        self._execution_callbacks: List[Callable] = []
        
    def execute(self, task: Task) -> bool:
        """
        Execute a task asynchronously.
        
        Args:
            task: Task to execute
            
        Returns:
            Success status
        """
        if not task.can_execute():
            return False
        
        with self._lock:
            if task.task_id in self._running_tasks:
                return False  # Task already running
            
            # Submit task for execution
            future = self._executor.submit(self._execute_task, task)
            self._running_tasks[task.task_id] = future
            
            return True
    
    def execute_sync(self, task: Task) -> TaskResult:
        """
        Execute a task synchronously.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        return self._execute_task(task)
    
    def _execute_task(self, task: Task) -> TaskResult:
        """
        Internal task execution logic.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        start_time = time.time()
        
        try:
            # Mark task as started
            task.mark_started()
            
            # Execute the task action
            if task.action:
                result_data = task.action(*task.action_args.get("args", []), 
                                         **task.action_args.get("kwargs", {}))
                
                result = TaskResult(
                    success=True,
                    data=result_data,
                    execution_time=time.time() - start_time
                )
                
                task.mark_completed(result)
                
                # Notify callbacks
                self._notify_callbacks(task, result)
                
                return result
            else:
                # No action defined
                error = "Task has no defined action"
                result = TaskResult(
                    success=False,
                    error=error,
                    execution_time=time.time() - start_time
                )
                
                task.mark_failed(error)
                self._notify_callbacks(task, result)
                
                return result
                
        except Exception as e:
            # Task execution failed
            error = str(e)
            result = TaskResult(
                success=False,
                error=error,
                execution_time=time.time() - start_time
            )
            
            task.mark_failed(error)
            self._notify_callbacks(task, result)
            
            return result
    
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            Success status
        """
        with self._lock:
            if task_id not in self._running_tasks:
                return False
            
            future = self._running_tasks[task_id]
            cancelled = future.cancel()
            
            if cancelled:
                del self._running_tasks[task_id]
                
            return cancelled
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get the status of a running task.
        
        Args:
            task_id: ID of task
            
        Returns:
            Task status or None if not found
        """
        with self._lock:
            if task_id not in self._running_tasks:
                return None
            
            future = self._running_tasks[task_id]
            if future.done():
                return "completed"
            elif future.cancelled():
                return "cancelled"
            else:
                return "running"
    
    def wait_for_completion(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for a task to complete.
        
        Args:
            task_id: ID of task to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if task completed, False if timeout or cancelled
        """
        with self._lock:
            if task_id not in self._running_tasks:
                return False
            
            future = self._running_tasks[task_id]
        
        try:
            future.result(timeout=timeout)
            return True
        except Exception:
            return False
    
    def add_execution_callback(self, callback: Callable) -> None:
        """
        Add a callback to be called on task completion.
        
        Args:
            callback: Callback function that takes (task, result)
        """
        self._execution_callbacks.append(callback)
    
    def _notify_callbacks(self, task: Task, result: TaskResult) -> None:
        """Notify all registered callbacks of task completion."""
        for callback in self._execution_callbacks:
            try:
                callback(task, result)
            except Exception as e:
                print(f"Error in execution callback: {e}")
    
    def get_running_tasks(self) -> List[str]:
        """
        Get IDs of currently running tasks.
        
        Returns:
            List of running task IDs
        """
        with self._lock:
            return list(self._running_tasks.keys())
    
    def get_executor_stats(self) -> Dict[str, any]:
        """
        Get executor statistics.
        
        Returns:
            Dictionary with executor statistics
        """
        with self._lock:
            return {
                "max_workers": self.max_workers,
                "running_tasks": len(self._running_tasks),
                "available_workers": self.max_workers - len(self._running_tasks)
            }
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.
        
        Args:
            wait: Whether to wait for running tasks to complete
        """
        self._executor.shutdown(wait=wait)
        
        with self._lock:
            self._running_tasks.clear()
    
    def cleanup_completed_tasks(self) -> int:
        """
        Clean up completed tasks from the running tasks map.
        
        Returns:
            Number of tasks cleaned up
        """
        with self._lock:
            completed_tasks = []
            
            for task_id, future in self._running_tasks.items():
                if future.done():
                    completed_tasks.append(task_id)
            
            for task_id in completed_tasks:
                del self._running_tasks[task_id]
            
            return len(completed_tasks)