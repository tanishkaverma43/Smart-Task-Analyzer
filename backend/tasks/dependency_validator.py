"""
Dependency validation utilities for detecting circular dependencies
and validating task relationships.
"""
from typing import List, Dict, Set, Tuple


class DependencyValidator:
    """Validates task dependencies and detects circular dependencies."""
    
    @staticmethod
    def detect_circular_dependencies(tasks: List[Dict]) -> Tuple[bool, List[int]]:
        """
        Detects circular dependencies in a list of tasks using DFS.
        
        This method identifies cycles in the dependency graph where tasks
        form a circular chain (e.g., Task A depends on B, B depends on C, C depends on A).
        
        Args:
            tasks: List of task dictionaries with 'id' and 'dependencies' fields
            
        Returns:
            Tuple of (has_cycle, cycle_path)
            - has_cycle: Boolean indicating if a cycle was detected
            - cycle_path: List of task IDs forming the cycle (empty if no cycle)
            
        Example:
            If Task 1 -> Task 2 -> Task 3 -> Task 1, returns (True, [1, 2, 3, 1])
        """
        if not tasks:
            return False, []
        
        graph = {}
        task_ids = set()
        
        for task in tasks:
            task_id = task.get('id')
            if task_id is None:
                continue  
            task_ids.add(task_id)
            dependencies = task.get('dependencies', [])
          
            graph[task_id] = [dep for dep in dependencies if dep is not None and dep in task_ids]
    
        visited = set()
        rec_stack = set()
        
        def dfs(node: int, path: List[int]) -> Tuple[bool, List[int]]:
            """
            Depth-first search to detect cycles.
            
            Uses recursion stack to detect back edges, which indicate cycles.
            """
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in graph:
                for neighbor in graph[node]:
                
                    if neighbor not in task_ids:
                        continue
                    
                    if neighbor not in visited:
            
                        has_cycle, cycle = dfs(neighbor, path.copy())
                        if has_cycle:
                            return True, cycle
                    elif neighbor in rec_stack:
                        cycle_start = path.index(neighbor)
                        cycle_path = path[cycle_start:] + [neighbor]
                        return True, cycle_path
            rec_stack.remove(node)
            return False, []
        for task_id in task_ids:
            if task_id not in visited:
                has_cycle, cycle_path = dfs(task_id, [])
                if has_cycle:
                    return True, cycle_path
        
        return False, []
    
    @staticmethod
    def validate_dependencies(tasks: List[Dict]) -> Tuple[bool, str]:
        """
        Validates that all dependency references exist in the task list.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        task_ids = {task.get('id') for task in tasks}
        
        for task in tasks:
            task_id = task.get('id')
            dependencies = task.get('dependencies', [])
            
            for dep_id in dependencies:
                if dep_id not in task_ids:
                    return False, f"Task {task_id} references non-existent dependency {dep_id}"
                
                if dep_id == task_id:
                    return False, f"Task {task_id} cannot depend on itself"
        
        return True, ""
    
    @staticmethod
    def count_dependents(tasks: List[Dict]) -> Dict[int, int]:
        """
        Counts how many tasks depend on each task.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Dictionary mapping task_id to count of dependent tasks
        """
        dependent_count = {task.get('id'): 0 for task in tasks}
        
        for task in tasks:
            dependencies = task.get('dependencies', [])
            for dep_id in dependencies:
                if dep_id in dependent_count:
                    dependent_count[dep_id] += 1
        
        return dependent_count


