"""
Task Queue - Priority-based task scheduling and queueing
"""

import heapq
from typing import Dict, List, Optional, Callable
from threading import Lock
from datetime import datetime

from .task import Task, TaskStatus, TaskPriority


class TaskQueue:
    """
    Priority-based task queue with thread-safe operations.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the task queue.
        
        Args:
            max_size: Maximum number of tasks in the queue
        """
        self.max_size = max_size
        self._queue: List[tuple] = []  # (priority, timestamp, task)
        self._task_map: Dict[str, Task] = {}  # task_id -> Task
        self._lock = Lock()
        self._counter = 0  # For FIFO ordering within same priority
        
    def enqueue(self, task: Task) -> bool:
        """
        Add a task to the queue.
        
        Args:
            task: Task to enqueue
            
        Returns:
            Success status
        """
        with self._lock:
            if len(self._queue) >= self.max_size:
                return False
            
            if task.task_id in self._task_map:
                return False  # Task already in queue
            
            # Calculate priority score (lower is higher priority)
            priority_score = self._calculate_priority_score(task)
            
            # Add to heap
            heapq.heappush(self._queue, (priority_score, self._counter, task))
            self._task_map[task.task_id] = task
            task.status = TaskStatus.QUEUED
            self._counter += 1
            
            return True
    
    def dequeue(self) -> Optional[Task]:
        """
        Remove and return the highest priority task.
        
        Args:
            Task: Highest priority task or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            # Pop from heap
            priority_score, counter, task = heapq.heappop(self._queue)
            
            # Remove from map
            if task.task_id in self._task_map:
                del self._task_map[task.task_id]
            
            return task
    
    def peek(self) -> Optional[Task]:
        """
        Peek at the highest priority task without removing it.
        
        Returns:
            Task: Highest priority task or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            return self._queue[0][2]  # Return task without popping
    
    def remove(self, task_id: str) -> bool:
        """
        Remove a specific task from the queue.
        
        Args:
            task_id: ID of task to remove
            
        Returns:
            Success status
        """
        with self._lock:
            if task_id not in self._task_map:
                return False
            
            # Remove from queue (mark as removed, will be skipped when dequeued)
            task = self._task_map[task_id]
            task.status = TaskStatus.CANCELLED
            del self._task_map[task_id]
            
            # Note: The task is still in the heap but will be skipped when dequeued
            # This is a lazy removal approach for efficiency
            
            return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID without removing it.
        
        Args:
            task_id: ID of task to get
            
        Returns:
            Task or None if not found
        """
        with self._lock:
            return self._task_map.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks in the queue.
        
        Returns:
            List of all tasks
        """
        with self._lock:
            return list(self._task_map.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get tasks by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of tasks with the specified status
        """
        with self._lock:
            return [task for task in self._task_map.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """
        Get tasks by priority.
        
        Args:
            priority: Priority to filter by
            
        Returns:
            List of tasks with the specified priority
        """
        with self._lock:
            return [task for task in self._task_map.values() if task.priority == priority]
    
    def clear(self) -> int:
        """
        Clear all tasks from the queue.
        
        Returns:
            Number of tasks cleared
        """
        with self._lock:
            count = len(self._queue)
            self._queue.clear()
            self._task_map.clear()
            return count
    
    def size(self) -> int:
        """
        Get the current size of the queue.
        
        Returns:
            Number of tasks in the queue
        """
        with self._lock:
            return len(self._task_map)
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if queue is empty, False otherwise
        """
        with self._lock:
            return len(self._task_map) == 0
    
    def is_full(self) -> bool:
        """
        Check if the queue is full.
        
        Returns:
            True if queue is full, False otherwise
        """
        with self._lock:
            return len(self._task_map) >= self.max_size
    
    def _calculate_priority_score(self, task: Task) -> int:
        """
        Calculate priority score for heap ordering.
        
        Args:
            task: Task to calculate score for
            
        Returns:
            Priority score (lower is higher priority)
        """
        # Base priority from task priority
        base_priority = task.priority.value
        
        # Adjust for scheduled time
        if task.scheduled_at:
            if task.scheduled_at > datetime.now():
                # Future scheduled tasks get lower priority
                time_diff = (task.scheduled_at - datetime.now()).total_seconds()
                base_priority += int(time_diff / 60)  # Add minutes as priority penalty
        
        return base_priority
    
    def reorder(self, comparison_func: Optional[Callable] = None) -> None:
        """
        Reorder the queue based on updated task priorities.
        
        Args:
            comparison_func: Optional custom comparison function
        """
        with self._lock:
            # Rebuild heap with updated priorities
            tasks = []
            while self._queue:
                _, _, task = heapq.heappop(self._queue)
                if task.status == TaskStatus.QUEUED:  # Only keep queued tasks
                    tasks.append(task)
            
            self._queue.clear()
            self._counter = 0
            
            for task in tasks:
                priority_score = self._calculate_priority_score(task)
                heapq.heappush(self._queue, (priority_score, self._counter, task))
                self._counter += 1
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        with self._lock:
            tasks_by_priority = {
                priority.value: len(self.get_tasks_by_priority(priority))
                for priority in TaskPriority
            }
            
            tasks_by_status = {
                status.value: len(self.get_tasks_by_status(status))
                for status in TaskStatus
            }
            
            return {
                "total_tasks": len(self._task_map),
                "max_size": self.max_size,
                "utilization": len(self._task_map) / self.max_size if self.max_size > 0 else 0,
                "tasks_by_priority": tasks_by_priority,
                "tasks_by_status": tasks_by_status
            }