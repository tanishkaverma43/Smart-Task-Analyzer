"""
Serializers for task data validation and transformation.
"""
from rest_framework import serializers
from datetime import datetime


class TaskSerializer(serializers.Serializer):
    """Serializer for task data with comprehensive validation."""
    
    id = serializers.IntegerField(required=True)
    title = serializers.CharField(required=True, max_length=255, allow_blank=False)
    due_date = serializers.DateField(required=True, format='%Y-%m-%d')
    estimated_hours = serializers.FloatField(required=True, min_value=0.1)
    importance = serializers.IntegerField(required=True, min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        allow_empty=True
    )
    
    def validate_id(self, value):
        """Validate task ID is positive."""
        if value is None:
            raise serializers.ValidationError("Task ID cannot be null")
        if value <= 0:
            raise serializers.ValidationError("Task ID must be a positive integer")
        return value
    
    def validate_title(self, value):
        """Validate title is not empty or just whitespace."""
        if value is None:
            raise serializers.ValidationError("Title cannot be null")
        if not isinstance(value, str):
            raise serializers.ValidationError("Title must be a string")
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Title cannot be empty or whitespace only")
        return stripped
    
    def validate_due_date(self, value):
        """Validate due date format and handle past dates."""
        if value is None:
            raise serializers.ValidationError("Due date cannot be null")
        
        if isinstance(value, str):
            try:
                parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise serializers.ValidationError(
                    f"Date must be in YYYY-MM-DD format, got: {value}"
                )
            return parsed_date
        

        if hasattr(value, 'year'):
            return value
        
        raise serializers.ValidationError(
            f"Invalid date format: {value}. Expected YYYY-MM-DD string or date object"
        )
    
    def validate_estimated_hours(self, value):
        """Validate estimated hours is positive and reasonable."""
        if value is None:
            raise serializers.ValidationError("Estimated hours cannot be null")
        
        try:
            hours = float(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                f"Estimated hours must be a number, got: {value} (type: {type(value).__name__})"
            )
        
        if hours <= 0:
            raise serializers.ValidationError(
                f"Estimated hours must be greater than 0, got: {hours}"
            )
        
        if hours > 1000: 
            raise serializers.ValidationError(
                f"Estimated hours seems unreasonably high: {hours}. Maximum allowed: 1000"
            )
        
        return hours
    
    def validate_importance(self, value):
        """Validate importance is in valid range."""
        if value is None:
            raise serializers.ValidationError("Importance cannot be null")
        
        try:
            importance = int(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                f"Importance must be an integer, got: {value} (type: {type(value).__name__})"
            )
        
        if not 1 <= importance <= 10:
            raise serializers.ValidationError(
                f"Importance must be between 1 and 10, got: {importance}"
            )
        
        return importance
    
    def validate_dependencies(self, value):
        """Validate dependencies list."""
        if value is None:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f"Dependencies must be a list, got: {type(value).__name__}"
            )
        
    
        validated_deps = []
        for dep_id in value:
            if dep_id is None:
                continue  
            try:
                dep_int = int(dep_id)
                if dep_int <= 0:
                    raise serializers.ValidationError(
                        f"Dependency ID must be positive, got: {dep_id}"
                    )
                validated_deps.append(dep_int)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Dependency ID must be an integer, got: {dep_id} (type: {type(dep_id).__name__})"
                )
        
        return validated_deps
    
    def validate(self, attrs):
        """Cross-field validation."""
      
        task_id = attrs.get('id')
        dependencies = attrs.get('dependencies', [])
        
        if task_id in dependencies:
            raise serializers.ValidationError(
                f"Task {task_id} cannot depend on itself"
            )
        
        return attrs


class TaskListSerializer(serializers.Serializer):
    """Serializer for a list of tasks with comprehensive validation."""
    
    tasks = TaskSerializer(many=True, required=True)
    
    def validate_tasks(self, value):
        """Validate tasks list."""
        if value is None:
            raise serializers.ValidationError("Tasks field cannot be null")
        
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f"Tasks must be a list, got: {type(value).__name__}"
            )
        
        if not value:
            raise serializers.ValidationError(
                "Tasks list cannot be empty"
            )
        
       
        task_ids = []
        for task in value:
            task_id = task.get('id') if isinstance(task, dict) else None
            if task_id is not None:
                task_ids.append(task_id)
        
        if len(task_ids) != len(set(task_ids)):
            duplicates = [tid for tid in task_ids if task_ids.count(tid) > 1]
            raise serializers.ValidationError(
                f"Duplicate task IDs found: {list(set(duplicates))}"
            )
        
        return value


class WeightConfigSerializer(serializers.Serializer):
    """Serializer for configurable algorithm weights."""
    
    urgency = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    importance = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    effort = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    dependencies = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    
    def validate(self, attrs):
        """Validate that weights sum to 1.0."""
   
        provided_weights = {k: v for k, v in attrs.items() if v is not None}
        
        if not provided_weights:
            
            return attrs
        
        
        all_keys = {'urgency', 'importance', 'effort', 'dependencies'}
        provided_keys = set(provided_weights.keys())
        
        if provided_keys and provided_keys != all_keys:
            missing = all_keys - provided_keys
            raise serializers.ValidationError(
                f"If providing weights, all four must be provided. Missing: {missing}"
            )
     
        total = sum(provided_weights.values())
        if abs(total - 1.0) > 0.01:
            raise serializers.ValidationError(
                f"Weights must sum to 1.0, but sum to {total:.4f}. "
                f"Provided weights: {provided_weights}"
            )
        
        return attrs


class ScoredTaskSerializer(serializers.Serializer):
    """Serializer for task with priority score."""
    
    id = serializers.IntegerField()
    title = serializers.CharField()
    due_date = serializers.DateField(format='%Y-%m-%d')
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.IntegerField())
    priority_score = serializers.FloatField()
    score_breakdown = serializers.DictField()


class TaskSuggestionSerializer(serializers.Serializer):
    """Serializer for task suggestion with explanation."""
    
    task = serializers.DictField()
    reason = serializers.CharField()


