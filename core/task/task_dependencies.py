"""
Task Dependencies - Manage task dependency graphs
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict, deque


class TaskDependencyGraph:
    """
    Graph structure for managing task dependencies.
    """
    
    def __init__(self):
        """Initialize the dependency graph."""
        self._graph: Dict[str, Set[str]] = defaultdict(set)  # task_id -> dependencies
        self._reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # task_id -> dependents
        self._nodes: Set[str] = set()
        
    def add_node(self, task_id: str) -> None:
        """
        Add a node to the graph.
        
        Args:
            task_id: Task ID to add
        """
        self._nodes.add(task_id)
        
    def add_dependency(self, task_id: str, depends_on: str) -> bool:
        """
        Add a dependency relationship.
        
        Args:
            task_id: Task that depends on another task
            depends_on: Task that task_id depends on
            
        Returns:
            Success status (False if creates cycle)
        """
        # Add nodes if they don't exist
        self._nodes.add(task_id)
        self._nodes.add(depends_on)
        
        # Check if this creates a cycle
        if self._creates_cycle(task_id, depends_on):
            return False
        
        # Add dependency
        self._graph[task_id].add(depends_on)
        self._reverse_graph[depends_on].add(task_id)
        
        return True
    
    def remove_dependency(self, task_id: str, depends_on: str) -> bool:
        """
        Remove a dependency relationship.
        
        Args:
            task_id: Task that depends on another task
            depends_on: Task that task_id depends on
            
        Returns:
            Success status
        """
        if depends_on in self._graph[task_id]:
            self._graph[task_id].remove(depends_on)
            self._reverse_graph[depends_on].remove(task_id)
            return True
        return False
    
    def remove_node(self, task_id: str) -> None:
        """
        Remove a node and all its relationships.
        
        Args:
            task_id: Task ID to remove
        """
        # Remove all dependencies this task has
        for dependent in self._reverse_graph[task_id]:
            self._graph[dependent].discard(task_id)
        
        # Remove all tasks that depend on this task
        for dependency in self._graph[task_id]:
            self._reverse_graph[dependency].discard(task_id)
        
        # Remove from graphs
        del self._graph[task_id]
        del self._reverse_graph[task_id]
        self._nodes.discard(task_id)
    
    def get_dependencies(self, task_id: str) -> Set[str]:
        """
        Get all dependencies for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Set of task IDs that this task depends on
        """
        return self._graph[task_id].copy()
    
    def get_dependents(self, task_id: str) -> Set[str]:
        """
        Get all tasks that depend on this task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Set of task IDs that depend on this task
        """
        return self._reverse_graph[task_id].copy()
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """
        Get tasks that are ready to execute (all dependencies completed).
        
        Args:
            completed_tasks: Set of completed task IDs
            
        Returns:
            List of task IDs that are ready to execute
        """
        ready_tasks = []
        
        for task_id in self._nodes:
            dependencies = self._graph[task_id]
            if dependencies.issubset(completed_tasks):
                ready_tasks.append(task_id)
        
        return ready_tasks
    
    def topological_sort(self) -> List[str]:
        """
        Perform topological sort of the graph.
        
        Returns:
            List of task IDs in topological order
        """
        in_degree = {node: len(self._graph[node]) for node in self._nodes}
        queue = deque([node for node in self._nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for dependent in self._reverse_graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return result
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains a cycle.
        
        Returns:
            True if cycle exists, False otherwise
        """
        visited = set()
        recursion_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in self._graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True
            
            recursion_stack.remove(node)
            return False
        
        for node in self._nodes:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def _creates_cycle(self, task_id: str, depends_on: str) -> bool:
        """
        Check if adding a dependency would create a cycle.
        
        Args:
            task_id: Task that depends on another task
            depends_on: Task that task_id depends on
            
        Returns:
            True if cycle would be created, False otherwise
        """
        # Temporarily add the dependency
        self._graph[task_id].add(depends_on)
        self._reverse_graph[depends_on].add(task_id)
        
        # Check for cycle
        has_cycle = self.has_cycle()
        
        # Remove the temporary dependency
        self._graph[task_id].remove(depends_on)
        self._reverse_graph[depends_on].remove(task_id)
        
        return has_cycle
    
    def get_execution_order(self) -> List[List[str]]:
        """
        Get execution order grouped by levels (tasks that can run in parallel).
        
        Returns:
            List of lists, where each inner list contains tasks that can run in parallel
        """
        if not self._nodes:
            return []
        
        # Get topological order
        topo_order = self.topological_sort()
        
        # Group by levels
        levels = []
        current_level = []
        completed_in_level = set()
        
        for task_id in topo_order:
            dependencies = self._graph[task_id]
            if dependencies.issubset(completed_in_level):
                current_level.append(task_id)
            else:
                if current_level:
                    levels.append(current_level)
                    completed_in_level.update(current_level)
                current_level = [task_id]
        
        if current_level:
            levels.append(current_level)
        
        return levels
    
    def get_critical_path(self) -> List[str]:
        """
        Get the critical path (longest path) in the dependency graph.
        
        Returns:
            List of task IDs on the critical path
        """
        if not self._nodes:
            return []
        
        # Find nodes with no dependencies (start nodes)
        start_nodes = [node for node in self._nodes if not self._graph[node]]
        
        # Find nodes with no dependents (end nodes)
        end_nodes = [node for node in self._nodes if not self._reverse_graph[node]]
        
        if not start_nodes or not end_nodes:
            return []
        
        # Find longest path from any start node to any end node
        max_path = []
        
        for start in start_nodes:
            path = self._find_longest_path(start, end_nodes)
            if len(path) > len(max_path):
                max_path = path
        
        return max_path
    
    def _find_longest_path(self, start: str, end_nodes: List[str]) -> List[str]:
        """
        Find longest path from start to any end node using DFS.
        
        Args:
            start: Starting node
            end_nodes: List of potential end nodes
            
        Returns:
            Longest path from start to an end node
        """
        longest_path = []
        
        def dfs(node: str, current_path: List[str]) -> None:
            nonlocal longest_path
            
            current_path.append(node)
            
            if node in end_nodes:
                if len(current_path) > len(longest_path):
                    longest_path = current_path.copy()
            else:
                for dependent in self._reverse_graph[node]:
                    dfs(dependent, current_path)
            
            current_path.pop()
        
        dfs(start, [])
        return longest_path
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get graph statistics.
        
        Returns:
            Dictionary with graph statistics
        """
        total_nodes = len(self._nodes)
        total_edges = sum(len(deps) for deps in self._graph.values())
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "has_cycle": self.has_cycle(),
            "average_dependencies": total_edges / total_nodes if total_nodes > 0 else 0
        }