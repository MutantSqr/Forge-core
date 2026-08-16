"""
Task Manager - Orchestrate task execution with dependencies and monitoring
"""

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import threading
import time

from .task import Task, TaskStatus, TaskPriority, TaskResult
from .task_queue import TaskQueue
from .task_executor import TaskExecutor
from .task_dependencies import TaskDependencyGraph


class TaskManager:
    """
    Main task manager that coordinates task queuing, execution, and dependency management.
    """
    
    def __init__(self, max_workers: int = 4, queue_size: int = 1000):
        """
        Initialize the task manager.
        
        Args:
            max_workers: Maximum number of parallel workers
            queue_size: Maximum size of the task queue
        """
        self.task_queue = TaskQueue(max_size=queue_size)
        self.task_executor = TaskExecutor(max_workers=max_workers)
        self.dependency_graph = TaskDependencyGraph()
        
        self._completed_tasks: Dict[str, Task] = {}
        self._failed_tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        
        # Add execution callback for dependency handling
        self.task_executor.add_execution_callback(self._on_task_complete)
        
    def start(self) -> None:
        """Start the task manager scheduler."""
        if self._running:
            return
            
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        
    def stop(self) -> None:
        """Stop the task manager scheduler."""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        
        self.task_executor.shutdown(wait=True)
    
    def create_task(self, 
                   name: str,
                   action: Optional[Callable] = None,
                   action_args: Optional[Dict] = None,
                   action_kwargs: Optional[Dict] = None,
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   dependencies: Optional[List[str]] = None,
                   timeout: Optional[int] = None,
                   max_retries: int = 0,
                   metadata: Optional[Dict] = None,
                   tags: Optional[List[str]] = None) -> Task:
        """
        Create a new task.
        
        Args:
            name: Task name
            action: Function to execute
            action_args: Positional arguments for action
            action_kwargs: Keyword arguments for action
            priority: Task priority
            dependencies: List of task IDs this task depends on
            timeout: Task timeout in seconds
            max_retries: Maximum number of retries
            metadata: Additional metadata
            tags: Task tags
            
        Returns:
            Created task
        """
        task = Task(
            name=name,
            action=action,
            action_args=action_args or {},
            action_kwargs=action_kwargs or {},
            priority=priority,
            dependencies=dependencies or [],
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {},
            tags=tags or []
        )
        
        # Add to dependency graph
        self.dependency_graph.add_node(task.task_id)
        for dep_id in task.dependencies:
            self.dependency_graph.add_dependency(task.task_id, dep_id)
        
        return task
    
    def submit_task(self, task: Task) -> bool:
        """
        Submit a task for execution.
        
        Args:
            task: Task to submit
            
        Returns:
            Success status
        """
        # Check if dependencies are satisfied
        if task.dependencies:
            completed_task_ids = set(self._completed_tasks.keys())
            if not set(task.dependencies).issubset(completed_task_ids):
                # Dependencies not met, queue for later
                return self.task_queue.enqueue(task)
        
        # Dependencies met or no dependencies, queue for execution
        return self.task_queue.enqueue(task)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            Success status
        """
        # Try to cancel from queue
        if self.task_queue.remove(task_id):
            return True
        
        # Try to cancel running task
        if self.task_executor.cancel(task_id):
            return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of task
            
        Returns:
            Task or None if not found
        """
        # Check queue
        task = self.task_queue.get_task(task_id)
        if task:
            return task
        
        # Check completed tasks
        with self._lock:
            if task_id in self._completed_tasks:
                return self._completed_tasks[task_id]
            
            if task_id in self._failed_tasks:
                return self._failed_tasks[task_id]
        
        return None
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get tasks by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of tasks with the specified status
        """
        if status == TaskStatus.COMPLETED:
            with self._lock:
                return list(self._completed_tasks.values())
        elif status == TaskStatus.FAILED:
            with self._lock:
                return list(self._failed_tasks.values())
        else:
            return self.task_queue.get_tasks_by_status(status)
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """
        Get tasks by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of tasks with the specified tag
        """
        tasks = []
        
        # Check queue
        for task in self.task_queue.get_all_tasks():
            if tag in task.tags:
                tasks.append(task)
        
        # Check completed tasks
        with self._lock:
            for task in self._completed_tasks.values():
                if tag in task.tags:
                    tasks.append(task)
        
        return tasks
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for a task to complete.
        
        Args:
            task_id: ID of task to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if task completed, False if timeout
        """
        return self.task_executor.wait_for_completion(task_id, timeout)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get task manager statistics.
        
        Returns:
            Dictionary with statistics
        """
        queue_stats = self.task_queue.get_statistics()
        executor_stats = self.task_executor.get_executor_stats()
        graph_stats = self.dependency_graph.get_stats()
        
        with self._lock:
            completed_count = len(self._completed_tasks)
            failed_count = len(self._failed_tasks)
        
        return {
            "queue": queue_stats,
            "executor": executor_stats,
            "dependency_graph": graph_stats,
            "completed_tasks": completed_count,
            "failed_tasks": failed_count,
            "total_tasks": queue_stats["total_tasks"] + completed_count + failed_count
        }
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                self._schedule_tasks()
                self._handle_retries()
                self._cleanup_completed_tasks()
                time.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
    
    def _schedule_tasks(self) -> None:
        """Schedule ready tasks for execution."""
        completed_task_ids = set(self._completed_tasks.keys())
        ready_tasks = self.dependency_graph.get_ready_tasks(completed_task_ids)
        
        for task_id in ready_tasks:
            task = self.task_queue.get_task(task_id)
            if task and task.can_execute():
                # Remove from queue and execute
                self.task_queue.remove(task_id)
                self.task_executor.execute(task)
    
    def _handle_retries(self) -> None:
        """Handle task retries."""
        with self._lock:
            retry_tasks = []
            
            for task_id, task in self._failed_tasks.items():
                if task.should_retry():
                    retry_tasks.append(task)
                    del self._failed_tasks[task_id]
        
        for task in retry_tasks:
            task.increment_retry()
            self.task_queue.enqueue(task)
    
    def _cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks from executor."""
        self.task_executor.cleanup_completed_tasks()
    
    def _on_task_complete(self, task: Task, result: TaskResult) -> None:
        """
        Handle task completion.
        
        Args:
            task: Completed task
            result: Task result
        """
        with self._lock:
            if result.success:
                self._completed_tasks[task.task_id] = task
            else:
                self._failed_tasks[task.task_id] = task
    
    def create_task_group(self, 
                         tasks: List[Task],
                         group_name: str,
                         wait_for_all: bool = True) -> str:
        """
        Create a group of related tasks.
        
        Args:
            tasks: List of tasks to group
            group_name: Name for the task group
            wait_for_all: Whether to wait for all tasks to complete
            
        Returns:
            Group ID
        """
        group_id = f"group_{group_name}_{datetime.now().isoformat()}"
        
        for task in tasks:
            task.metadata["group_id"] = group_id
            task.metadata["group_name"] = group_name
            self.submit_task(task)
        
        return group_id
    
    def get_group_tasks(self, group_id: str) -> List[Task]:
        """
        Get all tasks in a group.
        
        Args:
            group_id: Group ID
            
        Returns:
            List of tasks in the group
        """
        group_tasks = []
        
        # Check queue
        for task in self.task_queue.get_all_tasks():
            if task.metadata.get("group_id") == group_id:
                group_tasks.append(task)
        
        # Check completed tasks
        with self._lock:
            for task in self._completed_tasks.values():
                if task.metadata.get("group_id") == group_id:
                    group_tasks.append(task)
        
        return group_tasks
    
    def get_group_status(self, group_id: str) -> Dict[str, Any]:
        """
        Get status of a task group.
        
        Args:
            group_id: Group ID
            
        Returns:
            Dictionary with group status
        """
        tasks = self.get_group_tasks(group_id)
        
        if not tasks:
            return {"status": "not_found"}
        
        status_counts = {}
        for task in tasks:
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total = len(tasks)
        completed = status_counts.get("completed", 0)
        failed = status_counts.get("failed", 0)
        
        if completed == total:
            group_status = "completed"
        elif failed > 0:
            group_status = "partial_failure"
        elif completed > 0:
            group_status = "in_progress"
        else:
            group_status = "pending"
        
        return {
            "group_id": group_id,
            "status": group_status,
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "status_breakdown": status_counts
        }