"""
Priority calculation engine for task scoring.

The algorithm considers multiple factors:
- Urgency: Based on due date proximity (default 40% weight)
- Importance: User-provided rating (1-10) (default 30% weight)
- Effort: Rewards "quick wins" (default 15% weight)
- Dependencies: Tasks that block others rank higher (default 15% weight)

Balancing Urgent vs Important:
The algorithm balances competing priorities through configurable weights:
- Default: 40% urgency, 30% importance (urgency-weighted)
- Users can customize weights to prioritize importance over urgency if desired
- Overdue tasks get exponential urgency boost to ensure they're addressed
- High-importance tasks (8-10) still rank highly even if not urgent
- The weighted combination ensures both urgent and important tasks surface appropriately

Example configurations:
- Urgency-focused: urgency=0.5, importance=0.2, effort=0.15, dependencies=0.15
- Importance-focused: urgency=0.2, importance=0.5, effort=0.15, dependencies=0.15
- Balanced: urgency=0.35, importance=0.35, effort=0.15, dependencies=0.15
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Set
from .dependency_validator import DependencyValidator

WEIGHTS = {
    'urgency': 0.40,     
    'importance': 0.30,   
    'effort': 0.15,     
    'dependencies': 0.15  
}

MAX_SCORES = {
    'urgency': 100,
    'importance': 100,
    'effort': 100,
    'dependencies': 100
}


class PriorityCalculator:
    """
    Calculates priority scores for tasks based on multiple factors.
    
    The algorithm balances competing priorities (urgent vs important) through
    configurable weights. By default, urgency has higher weight (40%) than
    importance (30%), but this can be customized to match user preferences.
    
    Key features:
    - Handles overdue tasks with exponential urgency scoring
    - Validates all input data and provides clear error messages
    - Configurable weights allow users to prioritize urgency or importance
    - Detects and flags overdue tasks in metadata
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the calculator with optional custom weights.
        
        Args:
            weights: Optional dictionary of weight overrides
            
        Raises:
            ValueError: If weights don't sum to approximately 1.0 or contain invalid keys
        """
        self.weights = WEIGHTS.copy()
        if weights:
            valid_keys = set(WEIGHTS.keys())
            provided_keys = set(weights.keys())
            invalid_keys = provided_keys - valid_keys
            if invalid_keys:
                raise ValueError(f"Invalid weight keys: {invalid_keys}. Valid keys are: {valid_keys}")
            
            self.weights.update(weights)
            total_weight = sum(self.weights.values())
            if abs(total_weight - 1.0) > 0.01:
                raise ValueError(
                    f"Weights must sum to 1.0, but sum to {total_weight}. "
                    f"Current weights: {self.weights}"
                )
            
            for key, value in self.weights.items():
                if value < 0:
                    raise ValueError(f"Weight '{key}' must be non-negative, got {value}")
    
    @staticmethod
    def _is_weekend(d: date) -> bool:
        """Check if a date falls on a weekend (Saturday or Sunday)."""
        return d.weekday() >= 5  
    
    @staticmethod
    def _get_us_holidays(year: int) -> Set[date]:
        """
        Get US holidays for a given year.
        Can be extended to support other countries or custom holidays.
        """
        holidays = set()
        
        holidays.add(date(year, 1, 1))
        mlk_day = date(year, 1, 1)
        while mlk_day.weekday() != 0: 
            mlk_day += timedelta(days=1)
        holidays.add(mlk_day + timedelta(days=14)) 
     
        pres_day = date(year, 2, 1)
        while pres_day.weekday() != 0:
            pres_day += timedelta(days=1)
        holidays.add(pres_day + timedelta(days=14))
        
        mem_day = date(year, 5, 31)
        while mem_day.weekday() != 0:
            mem_day -= timedelta(days=1)
        holidays.add(mem_day)
        holidays.add(date(year, 7, 4))

    
        labor_day = date(year, 9, 1)
        while labor_day.weekday() != 0:
            labor_day += timedelta(days=1)
        holidays.add(labor_day)
        
    
        col_day = date(year, 10, 1)
        while col_day.weekday() != 0:
            col_day += timedelta(days=1)
        holidays.add(col_day + timedelta(days=7))
        

        holidays.add(date(year, 11, 11))
        

        thanks = date(year, 11, 1)
        while thanks.weekday() != 3: 
            thanks += timedelta(days=1)
        holidays.add(thanks + timedelta(days=21))
        
        holidays.add(date(year, 12, 25))
        
        return holidays
    
    @staticmethod
    def _count_working_days(start_date: date, end_date: date) -> int:
        """
        Count working days (excluding weekends and holidays) between two dates.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Number of working days
        """
        if start_date > end_date:
            return 0
        
        working_days = 0
        current = start_date
        holidays = PriorityCalculator._get_us_holidays(current.year)
    
        if end_date.year > current.year:
            holidays.update(PriorityCalculator._get_us_holidays(end_date.year))
        
        while current <= end_date:
            if not PriorityCalculator._is_weekend(current) and current not in holidays:
                working_days += 1
            current += timedelta(days=1)
        
        return working_days
    
    def calculate_urgency_score(self, due_date: date) -> float:
        """
        Calculate urgency score based on due date, considering weekends and holidays.
        
        This method uses working days (excluding weekends and holidays) to calculate
        urgency, making it more realistic for business contexts where tasks can't
        be completed on non-working days.
        
        Score distribution:
        - Overdue: 80-100 (exponentially increases with days overdue)
        - Due today: 100
        - Due within 3 working days: 70-90
        - Due within week: 50-70
        - Due within 2 weeks: 30-50
        - Further out: 0-30
        
        Args:
            due_date: The task's due date
            
        Returns:
            Urgency score (0-100)
        """
        today = date.today()
        calendar_days = (due_date - today).days
        working_days = self._count_working_days(today, due_date)
        
        if calendar_days < 0:
    
            days_overdue = abs(calendar_days)
       
            score = min(100, 80 + (days_overdue ** 1.5) * 2)
            return score
        elif calendar_days == 0:
      
            return 100
        elif working_days <= 0:
          
            return 95
        elif working_days <= 3:
        
            return 90 - (working_days * 7)
        elif working_days <= 7:
            
            return 70 - ((working_days - 3) * 5)
        elif working_days <= 14:
         
            return 50 - ((working_days - 7) * 3)
        elif working_days <= 30:
          
            return 30 - ((working_days - 14) * 1.5)
        else:
           
            return max(0, 10 - (working_days - 30) * 0.2)
    
    def calculate_importance_score(self, importance: int) -> float:
        """
        Calculate importance score from user rating.
        
        Args:
            importance: User rating (1-10 scale)
            
        Returns:
            Importance score (0-100)
        """
    
        importance = max(1, min(10, importance))
       
        return (importance / 10) * 100
    
    def calculate_effort_score(self, estimated_hours: float) -> float:
        """
        Calculate effort score - rewards "quick wins".
        
        Score distribution:
        - < 1 hour: 100
        - 1-2 hours: 90
        - 2-4 hours: 70
        - 4-8 hours: 50
        - 8-16 hours: 30
        - > 16 hours: 10
        
        Args:
            estimated_hours: Estimated time to complete
            
        Returns:
            Effort score (0-100)
        """
        if estimated_hours < 1:
            return 100
        elif estimated_hours <= 2:
            return 90 - ((estimated_hours - 1) * 10)
        elif estimated_hours <= 4:
            return 70 - ((estimated_hours - 2) * 10)
        elif estimated_hours <= 8:
            return 50 - ((estimated_hours - 4) * 5)
        elif estimated_hours <= 16:
            return 30 - ((estimated_hours - 8) * 2.5)
        else:
            return max(0, 10 - (estimated_hours - 16) * 0.5)
    
    def calculate_dependency_score(self, dependent_count: int) -> float:
        """
        Calculate dependency score based on how many tasks depend on this one.
        
        Score distribution:
        - 0 dependents: 0
        - 1 dependent: 30
        - 2 dependents: 50
        - 3 dependents: 65
        - 4 dependents: 75
        - 5+ dependents: 80-100
        
        Args:
            dependent_count: Number of tasks that depend on this task
            
        Returns:
            Dependency score (0-100)
        """
        if dependent_count == 0:
            return 0
        elif dependent_count == 1:
            return 30
        elif dependent_count == 2:
            return 50
        elif dependent_count == 3:
            return 65
        elif dependent_count == 4:
            return 75
        else:
            # Diminishing returns after 5
            return min(100, 80 + (dependent_count - 5) * 4)
    
    def calculate_priority_score(
        self,
        task: Dict,
        dependent_count: int = 0
    ) -> Dict:
        """
        Calculate overall priority score for a task.
        
        Args:
            task: Task dictionary with required fields
            dependent_count: Number of tasks depending on this task
            
        Returns:
            Dictionary with priority_score, score_breakdown, and metadata (is_overdue, days_overdue)
            
        Raises:
            ValueError: If required task fields are missing or invalid
        """
 
        due_date_str = task.get('due_date')
        if due_date_str is None:
            raise ValueError("Task missing required field: 'due_date'")
        
        try:
            if isinstance(due_date_str, str):
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            else:
                due_date = due_date_str
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid due_date format: {due_date_str}. Expected YYYY-MM-DD format. Error: {str(e)}")
        

        today = date.today()
        days_until_due = (due_date - today).days
        is_overdue = days_until_due < 0
        days_overdue = abs(days_until_due) if is_overdue else 0
      
        importance = task.get('importance')
        if importance is None:
            raise ValueError("Task missing required field: 'importance'")
        try:
            importance = int(importance)
            if not (1 <= importance <= 10):
                raise ValueError(f"Importance must be between 1 and 10, got {importance}")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid importance value: {task.get('importance')}. Must be integer between 1-10")
        
        estimated_hours = task.get('estimated_hours')
        if estimated_hours is None:
            raise ValueError("Task missing required field: 'estimated_hours'")
        try:
            estimated_hours = float(estimated_hours)
            if estimated_hours <= 0:
                raise ValueError(f"Estimated hours must be positive, got {estimated_hours}")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid estimated_hours value: {task.get('estimated_hours')}. Must be positive number")
       
        urgency_score = self.calculate_urgency_score(due_date)
        importance_score = self.calculate_importance_score(importance)
        effort_score = self.calculate_effort_score(estimated_hours)
        dependency_score = self.calculate_dependency_score(dependent_count)
        weighted_urgency = urgency_score * self.weights['urgency']
        weighted_importance = importance_score * self.weights['importance']
        weighted_effort = effort_score * self.weights['effort']
        weighted_dependencies = dependency_score * self.weights['dependencies']
        
        total_score = (
            weighted_urgency +
            weighted_importance +
            weighted_effort +
            weighted_dependencies
        )
        
        return {
            'priority_score': round(total_score, 2),
            'score_breakdown': {
                'urgency_score': round(weighted_urgency, 2),
                'importance_score': round(weighted_importance, 2),
                'effort_score': round(weighted_effort, 2),
                'dependency_score': round(weighted_dependencies, 2),
                'urgency_raw': round(urgency_score, 2),
                'importance_raw': round(importance_score, 2),
                'effort_raw': round(effort_score, 2),
                'dependency_raw': round(dependency_score, 2)
            },
            'metadata': {
                'is_overdue': is_overdue,
                'days_overdue': days_overdue,
                'days_until_due': days_until_due
            }
        }
    
    def analyze_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Analyze and score a list of tasks.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            List of tasks with priority scores, sorted by priority (highest first)
            
        Raises:
            ValueError: If tasks list is empty or contains invalid tasks
        """
        if not tasks:
            raise ValueError("Tasks list cannot be empty")
        required_fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance']
        for task in tasks:
            missing_fields = [field for field in required_fields if field not in task or task[field] is None]
            if missing_fields:
                task_id = task.get('id', 'unknown')
                raise ValueError(f"Task {task_id} missing required fields: {', '.join(missing_fields)}")

        validator = DependencyValidator()
        dependent_counts = validator.count_dependents(tasks)
        scored_tasks = []
        errors = []
        for task in tasks:
            try:
                task_id = task.get('id')
                dependent_count = dependent_counts.get(task_id, 0)
                
                score_data = self.calculate_priority_score(task, dependent_count)
                scored_task = task.copy()
                scored_task.update(score_data)
                scored_tasks.append(scored_task)
            except ValueError as e:
                errors.append({
                    'task_id': task.get('id', 'unknown'),
                    'task_title': task.get('title', 'unknown'),
                    'error': str(e)
                })

        if errors:
            error_messages = [f"Task {e['task_id']} ({e['task_title']}): {e['error']}" for e in errors]
            raise ValueError(f"Failed to analyze {len(errors)} task(s):\n" + "\n".join(error_messages))
        scored_tasks.sort(key=lambda t: t['priority_score'], reverse=True)
        
        return scored_tasks
    
    def generate_task_explanation(self, task: Dict) -> str:
        """
        Generate a human-readable explanation for why a task was prioritized.
        
        Args:
            task: Task with calculated scores
            
        Returns:
            Explanation string
        """
        explanations = []
        due_date_str = task.get('due_date')
        if isinstance(due_date_str, str):
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            due_date = due_date_str
        
        today = date.today()
        days_until_due = (due_date - today).days
        if days_until_due < 0:
            days_overdue = abs(days_until_due)
            if days_overdue == 1:
                explanations.append("overdue by 1 day (CRITICAL)")
            elif days_overdue <= 7:
                explanations.append(f"overdue by {days_overdue} days (URGENT)")
            else:
                explanations.append(f"overdue by {days_overdue} days (CRITICAL - requires immediate attention)")
        elif days_until_due == 0:
            explanations.append("due TODAY (URGENT)")
        elif days_until_due <= 3:
            explanations.append(f"due in {days_until_due} day(s) (URGENT)")
        
       
        importance = task.get('importance', 5)
        if importance >= 8:
            explanations.append(f"high importance ({importance}/10)")
        elif importance >= 6:
            explanations.append(f"medium importance ({importance}/10)")
     
        estimated_hours = task.get('estimated_hours', 4)
        if estimated_hours <= 2:
            explanations.append(f"quick win ({estimated_hours}h)")
     
        breakdown = task.get('score_breakdown', {})
        dependency_raw = breakdown.get('dependency_raw', 0)
        if dependency_raw > 0:
          
            if dependency_raw >= 50:
                explanations.append("blocks multiple tasks")
            else:
                explanations.append("blocks other task(s)")
        
        if not explanations:
            explanations.append(f"balanced priority (score: {task.get('priority_score', 0):.1f})")
        
        return "This task is " + ", ".join(explanations) + "."
    
    def get_balance_explanation(self) -> Dict[str, str]:
        """
        Get explanation of how the algorithm balances urgent vs important priorities.
        
        Returns:
            Dictionary with balance explanation
        """
        urgency_weight = self.weights['urgency']
        importance_weight = self.weights['importance']
        
        if urgency_weight > importance_weight:
            balance_type = "urgency-focused"
            balance_desc = f"Urgency ({urgency_weight*100:.0f}%) is weighted higher than importance ({importance_weight*100:.0f}%), so urgent tasks will generally rank higher."
        elif importance_weight > urgency_weight:
            balance_type = "importance-focused"
            balance_desc = f"Importance ({importance_weight*100:.0f}%) is weighted higher than urgency ({urgency_weight*100:.0f}%), so important tasks will generally rank higher."
        else:
            balance_type = "balanced"
            balance_desc = f"Urgency and importance are equally weighted ({urgency_weight*100:.0f}% each), providing balanced prioritization."
        
        return {
            'balance_type': balance_type,
            'description': balance_desc,
            'weights': self.weights.copy(),
            'note': 'Overdue tasks still receive exponential urgency boost regardless of weights'
        }


