"""
API views for task analysis and suggestions.
"""
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Task, TaskFeedback
from .serializers import (
    TaskListSerializer,
    ScoredTaskSerializer,
    TaskSuggestionSerializer,
    WeightConfigSerializer
)
from .scoring import PriorityCalculator, WEIGHTS, DependencyValidator


class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/
    
    Analyzes a list of tasks and returns them sorted by priority score.
    """
    
    def post(self, request):
        """
        Analyze and prioritize tasks.
        
        Request body:
        {
            "tasks": [
                {
                    "id": 1,
                    "title": "Fix login bug",
                    "due_date": "2025-11-30",
                    "estimated_hours": 3,
                    "importance": 8,
                    "dependencies": []
                },
                ...
            ]
        }
        
        Returns:
        {
            "tasks": [
                {
                    ...task fields...,
                    "priority_score": 85.5,
                    "score_breakdown": {...}
                },
                ...
            ]
        }
        """

        serializer = TaskListSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid input data',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = serializer.validated_data['tasks']
        
    
        validator = DependencyValidator()
    
        is_valid, error_msg = validator.validate_dependencies(tasks)
        if not is_valid:
            return Response(
                {
                    'error': 'Invalid dependencies',
                    'message': error_msg
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        has_cycle, cycle_path = validator.detect_circular_dependencies(tasks)
        if has_cycle:
            return Response(
                {
                    'error': 'Circular dependency detected',
                    'cycle': cycle_path,
                    'message': f"Circular dependency found: {' -> '.join(map(str, cycle_path))}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
     
        custom_weights = request.data.get('weights')
        weights = None
        if custom_weights:
            weight_serializer = WeightConfigSerializer(data=custom_weights)
            if not weight_serializer.is_valid():
                return Response(
                    {
                        'error': 'Invalid weight configuration',
                        'details': weight_serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            weights = weight_serializer.validated_data
        
       
        try:
            calculator = PriorityCalculator(weights=weights)
            scored_tasks = calculator.analyze_tasks(tasks)
            
            return Response(
                {'tasks': scored_tasks},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {
                    'error': 'Invalid task data',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Failed to analyze tasks',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/
    POST /api/tasks/suggest/
    
    Returns the top 3 tasks to work on with explanations.
    GET: Uses tasks from database
    POST: Uses tasks from request body
    """
    
    def get(self, request):
        """
        Get top 3 task suggestions from database tasks.
        
        Returns:
        {
            "suggestions": [
                {
                    "task": {...},
                    "reason": "This task is overdue by 5 days, has high importance..."
                },
                ...
            ]
        }
        """
   
        tasks = Task.objects.all()
        
        if not tasks.exists():
            return Response(
                {'error': 'No tasks found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        

        task_list = [task.to_dict() for task in tasks]
        
     
        validator = DependencyValidator()
        
       
        is_valid, error_msg = validator.validate_dependencies(task_list)
        if not is_valid:
            return Response(
                {
                    'error': 'Invalid dependencies',
                    'message': error_msg
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
    
        has_cycle, cycle_path = validator.detect_circular_dependencies(task_list)
        if has_cycle:
            return Response(
                {
                    'error': 'Circular dependency detected',
                    'cycle': cycle_path,
                    'message': f"Circular dependency found: {' -> '.join(map(str, cycle_path))}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
       
        custom_weights = request.query_params.get('weights')
        weights = None
        if custom_weights:
            try:
                import json
                weights_dict = json.loads(custom_weights)
                weight_serializer = WeightConfigSerializer(data=weights_dict)
                if not weight_serializer.is_valid():
                    return Response(
                        {
                            'error': 'Invalid weight configuration',
                            'details': weight_serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                weights = weight_serializer.validated_data
            except (json.JSONDecodeError, ValueError) as e:
                return Response(
                    {
                        'error': 'Invalid weight configuration format',
                        'message': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
      
        try:
            calculator = PriorityCalculator(weights=weights)
            scored_tasks = calculator.analyze_tasks(task_list)
            
            
            top_tasks = scored_tasks[:3]
            
           
            suggestions = []
            for task in top_tasks:
                explanation = calculator.generate_task_explanation(task)
                task_dict = {
                    'id': task['id'],
                    'title': task['title'],
                    'due_date': task['due_date'].strftime('%Y-%m-%d') if hasattr(task['due_date'], 'strftime') else task['due_date'],
                    'priority_score': task['priority_score']
                }
               
                if 'metadata' in task:
                    task_dict['is_overdue'] = task['metadata'].get('is_overdue', False)
                    task_dict['days_overdue'] = task['metadata'].get('days_overdue', 0)
                
                suggestions.append({
                    'task': task_dict,
                    'reason': explanation
                })
            
            return Response(
                {'suggestions': suggestions},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {
                    'error': 'Invalid task data',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Failed to generate suggestions',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Get top 3 task suggestions.
        
        Request body: Same as analyze endpoint
        
        Returns:
        {
            "suggestions": [
                {
                    "task": {...},
                    "reason": "This task is overdue by 5 days, has high importance..."
                },
                ...
            ]
        }
        """
        
        serializer = TaskListSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid input data',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = serializer.validated_data['tasks']
        
       
        validator = DependencyValidator()
        
       
        is_valid, error_msg = validator.validate_dependencies(tasks)
        if not is_valid:
            return Response(
                {
                    'error': 'Invalid dependencies',
                    'message': error_msg
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
       
        has_cycle, cycle_path = validator.detect_circular_dependencies(tasks)
        if has_cycle:
            return Response(
                {
                    'error': 'Circular dependency detected',
                    'cycle': cycle_path,
                    'message': f"Circular dependency found: {' -> '.join(map(str, cycle_path))}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
    
        custom_weights = request.data.get('weights')
        weights = None
        if custom_weights:
            weight_serializer = WeightConfigSerializer(data=custom_weights)
            if not weight_serializer.is_valid():
                return Response(
                    {
                        'error': 'Invalid weight configuration',
                        'details': weight_serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            weights = weight_serializer.validated_data
        
        try:
            calculator = PriorityCalculator(weights=weights)
            scored_tasks = calculator.analyze_tasks(tasks)
            
        
            top_tasks = scored_tasks[:3]
          
            suggestions = []
            for task in top_tasks:
                explanation = calculator.generate_task_explanation(task)
                task_dict = {
                    'id': task['id'],
                    'title': task['title'],
                    'due_date': task['due_date'].strftime('%Y-%m-%d') if hasattr(task['due_date'], 'strftime') else task['due_date'],
                    'priority_score': task['priority_score']
                }
              
                if 'metadata' in task:
                    task_dict['is_overdue'] = task['metadata'].get('is_overdue', False)
                    task_dict['days_overdue'] = task['metadata'].get('days_overdue', 0)
                
                suggestions.append({
                    'task': task_dict,
                    'reason': explanation
                })
            
            return Response(
                {'suggestions': suggestions},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {
                    'error': 'Invalid task data',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Failed to generate suggestions',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Simple health check endpoint."""
    
    def get(self, request):
        """Health check."""
        return Response(
            {
                'status': 'healthy',
                'service': 'Smart Task Analyzer',
                'version': '1.0.0'
            },
            status=status.HTTP_200_OK
        )


class TaskListCreateView(APIView):
    """
    GET /api/tasks/ - List all tasks
    POST /api/tasks/ - Create a new task
    """
    
    def get(self, request):
        """Get all tasks from database."""
        tasks = Task.objects.all()
        task_list = [task.to_dict() for task in tasks]
        return Response(
            {'tasks': task_list, 'count': len(task_list)},
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        """Create a new task in database."""
        data = request.data
        
     
        required_fields = ['title', 'due_date', 'estimated_hours', 'importance']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
         
            task = Task.objects.create(
                title=data['title'],
                due_date=data['due_date'],
                estimated_hours=float(data['estimated_hours']),
                importance=int(data['importance']),
                dependencies=data.get('dependencies', [])
            )
            
            return Response(
                {
                    'message': 'Task created successfully',
                    'task': task.to_dict()
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to create task', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TaskDetailView(APIView):
    """
    GET /api/tasks/<id>/ - Retrieve a task
    PUT /api/tasks/<id>/ - Update a task
    DELETE /api/tasks/<id>/ - Delete a task
    """
    
    def get(self, request, pk):
        """Get a single task by ID."""
        task = get_object_or_404(Task, pk=pk)
        return Response(task.to_dict(), status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Update a task."""
        task = get_object_or_404(Task, pk=pk)
        data = request.data
        
        try:
      
            if 'title' in data:
                task.title = data['title']
            if 'due_date' in data:
                task.due_date = data['due_date']
            if 'estimated_hours' in data:
                task.estimated_hours = float(data['estimated_hours'])
            if 'importance' in data:
                task.importance = int(data['importance'])
            if 'dependencies' in data:
                task.dependencies = data['dependencies']
            
            task.save()
            
            return Response(
                {
                    'message': 'Task updated successfully',
                    'task': task.to_dict()
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to update task', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, pk):
        """Delete a task."""
        task = get_object_or_404(Task, pk=pk)
        task_dict = task.to_dict()
        task.delete()
        
        return Response(
            {
                'message': 'Task deleted successfully',
                'task': task_dict
            },
            status=status.HTTP_200_OK
        )


class TaskBulkCreateView(APIView):
    """
    POST /api/tasks/bulk/ - Create multiple tasks at once
    """
    
    def post(self, request):
        """Create multiple tasks from JSON array."""
        data = request.data
        
        if 'tasks' not in data or not isinstance(data['tasks'], list):
            return Response(
                {'error': 'Request must contain a "tasks" array'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks_data = data['tasks']
        created_tasks = []
        errors = []
        
        for idx, task_data in enumerate(tasks_data):
            try:
              
                required_fields = ['title', 'due_date', 'estimated_hours', 'importance']
                for field in required_fields:
                    if field not in task_data:
                        raise ValueError(f'Missing required field: {field}')
                
         
                task = Task.objects.create(
                    title=task_data['title'],
                    due_date=task_data['due_date'],
                    estimated_hours=float(task_data['estimated_hours']),
                    importance=int(task_data['importance']),
                    dependencies=task_data.get('dependencies', [])
                )
                created_tasks.append(task.to_dict())
                
            except Exception as e:
                errors.append({
                    'index': idx,
                    'task': task_data.get('title', 'Unknown'),
                    'error': str(e)
                })
        
        response_data = {
            'created': len(created_tasks),
            'tasks': created_tasks
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['failed'] = len(errors)
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED if created_tasks else status.HTTP_400_BAD_REQUEST
        )


class TaskClearAllView(APIView):
    """
    DELETE /api/tasks/clear/ - Delete all tasks
    """
    
    def delete(self, request):
        """Delete all tasks from database and reset ID sequence."""
        from django.db import connection
        
        count = Task.objects.count()
        Task.objects.all().delete()
        
        # Reset SQLite auto-increment sequence so new tasks start from ID 1
        with connection.cursor() as cursor:
            # Delete the sequence entry for tasks table
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks_task'")
        
        return Response(
            {
                'message': f'Successfully deleted {count} task(s). ID sequence reset.',
                'deleted_count': count
            },
            status=status.HTTP_200_OK
        )


class WeightConfigView(APIView):
    """
    GET /api/tasks/weights/ - Get default weights
    POST /api/tasks/weights/ - Validate custom weights
    """
    
    def get(self, request):
        """Get default weight configuration."""
        from .scoring import WEIGHTS
        return Response(
            {
                'default_weights': WEIGHTS,
                'description': {
                    'urgency': 'Weight for urgency factor (based on due date proximity)',
                    'importance': 'Weight for importance factor (user-provided 1-10 rating)',
                    'effort': 'Weight for effort factor (rewards quick wins)',
                    'dependencies': 'Weight for dependency factor (tasks that block others)'
                },
                'note': 'Weights must sum to 1.0. Use these in analyze/suggest endpoints via "weights" parameter.'
            },
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        """Validate custom weight configuration."""
        serializer = WeightConfigSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid weight configuration',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        weights = serializer.validated_data
       
        try:
            calculator = PriorityCalculator(weights=weights)
            return Response(
                {
                    'message': 'Weight configuration is valid',
                    'weights': weights,
                    'note': 'Use these weights in analyze/suggest endpoints via "weights" parameter'
                },
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {
                    'error': 'Invalid weight configuration',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AnalyzeStoredTasksView(APIView):
    """
    GET /api/tasks/analyze-stored/ - Analyze all tasks from database
    """
    
    def get(self, request):
        """Analyze tasks stored in database."""
        tasks = Task.objects.all()
        
        if not tasks.exists():
            return Response(
                {'error': 'No tasks found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task_list = [task.to_dict() for task in tasks]
        
      
        validator = DependencyValidator()
     
        is_valid, error_msg = validator.validate_dependencies(task_list)
        if not is_valid:
            return Response(
                {
                    'error': 'Invalid dependencies',
                    'message': error_msg
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        

        has_cycle, cycle_path = validator.detect_circular_dependencies(task_list)
        if has_cycle:
            return Response(
                {
                    'error': 'Circular dependency detected',
                    'cycle': cycle_path,
                    'message': f"Circular dependency found: {' -> '.join(map(str, cycle_path))}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
   
        custom_weights = request.query_params.get('weights')
        weights = None
        if custom_weights:
            try:
                import json
                weights_dict = json.loads(custom_weights)
                weight_serializer = WeightConfigSerializer(data=weights_dict)
                if not weight_serializer.is_valid():
                    return Response(
                        {
                            'error': 'Invalid weight configuration',
                            'details': weight_serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                weights = weight_serializer.validated_data
            except (json.JSONDecodeError, ValueError) as e:
                return Response(
                    {
                        'error': 'Invalid weight configuration format',
                        'message': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        

        try:
            calculator = PriorityCalculator(weights=weights)
            scored_tasks = calculator.analyze_tasks(task_list)
            
            return Response(
                {'tasks': scored_tasks},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {
                    'error': 'Invalid task data',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Failed to analyze tasks',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DependencyGraphView(APIView):
    """
    GET /api/tasks/dependency-graph/ - Get dependency graph data for visualization
    POST /api/tasks/dependency-graph/ - Get dependency graph from request body
    """
    
    def _build_graph_data(self, tasks):
        """Build graph data structure for visualization."""
        validator = DependencyValidator()
        
     
        has_cycle, cycle_path = validator.detect_circular_dependencies(tasks)
        cycle_set = set(cycle_path) if has_cycle else set()
        

        nodes = []
        edges = []
        task_map = {task.get('id'): task for task in tasks}
        
        for task in tasks:
            task_id = task.get('id')
            if task_id is None:
                continue
            
        
            is_in_cycle = task_id in cycle_set
            
            nodes.append({
                'id': task_id,
                'label': f"{task_id}: {task.get('title', 'Untitled')[:30]}",
                'title': task.get('title', 'Untitled'),
                'inCycle': is_in_cycle,
                'dependencies': task.get('dependencies', [])
            })
            
    
            for dep_id in task.get('dependencies', []):
                if dep_id in task_map:
            
                    edge_in_cycle = is_in_cycle and dep_id in cycle_set
                    edges.append({
                        'from': dep_id,
                        'to': task_id,
                        'arrows': 'to',
                        'color': {'color': '#ef4444' if edge_in_cycle else '#64748b'},
                        'inCycle': edge_in_cycle
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'hasCycle': has_cycle,
            'cyclePath': cycle_path if has_cycle else []
        }
    
    def get(self, request):
        """Get dependency graph from database tasks."""
        tasks = Task.objects.all()
        
        if not tasks.exists():
            return Response(
                {'error': 'No tasks found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task_list = [task.to_dict() for task in tasks]
        graph_data = self._build_graph_data(task_list)
        
        return Response(graph_data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Get dependency graph from request body."""
        serializer = TaskListSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid input data',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = serializer.validated_data['tasks']
        graph_data = self._build_graph_data(tasks)
        
        return Response(graph_data, status=status.HTTP_200_OK)


class EisenhowerMatrixView(APIView):
    """
    GET /api/tasks/eisenhower-matrix/ - Get tasks organized in Eisenhower Matrix
    POST /api/tasks/eisenhower-matrix/ - Get matrix from request body
    """
    
    def _categorize_task(self, task, calculator):
        """
        Categorize task into Eisenhower Matrix quadrants.
        
        Quadrants:
        - Q1 (Urgent & Important): High urgency + High importance
        - Q2 (Not Urgent & Important): Low urgency + High importance
        - Q3 (Urgent & Not Important): High urgency + Low importance
        - Q4 (Not Urgent & Not Important): Low urgency + Low importance
        """
        from datetime import datetime, date
        
       
        due_date_str = task.get('due_date')
        if isinstance(due_date_str, str):
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            due_date = due_date_str
        
        urgency_score = calculator.calculate_urgency_score(due_date)
        importance_score = calculator.calculate_importance_score(task.get('importance', 5))
        
    
        is_urgent = urgency_score >= 50
        is_important = importance_score >= 50
        
        if is_urgent and is_important:
            quadrant = 'Q1'
        elif not is_urgent and is_important:
            quadrant = 'Q2' 
        elif is_urgent and not is_important:
            quadrant = 'Q3'  
        else:
            quadrant = 'Q4' 
        
        return {
            'quadrant': quadrant,
            'urgency_score': urgency_score,
            'importance_score': importance_score
        }
    
    def _build_matrix(self, tasks, calculator):
        """Build Eisenhower Matrix data structure."""
        matrix = {
            'Q1': [], 
            'Q2': [],  
            'Q3': [],  
            'Q4': []  
        }
        
        for task in tasks:
            category = self._categorize_task(task, calculator)
            quadrant = category['quadrant']
            
            task_with_category = task.copy()
            task_with_category.update(category)
            matrix[quadrant].append(task_with_category)
        
        return matrix
    
    def get(self, request):
        """Get Eisenhower Matrix from database tasks."""
        tasks = Task.objects.all()
        
        if not tasks.exists():
            return Response(
                {'error': 'No tasks found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task_list = [task.to_dict() for task in tasks]
        
       
        custom_weights = request.query_params.get('weights')
        weights = None
        if custom_weights:
            try:
                import json
                weights_dict = json.loads(custom_weights)
                weight_serializer = WeightConfigSerializer(data=weights_dict)
                if weight_serializer.is_valid():
                    weights = weight_serializer.validated_data
            except (json.JSONDecodeError, ValueError):
                pass
        
        calculator = PriorityCalculator(weights=weights)
        matrix = self._build_matrix(task_list, calculator)
        
        return Response({'matrix': matrix}, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Get Eisenhower Matrix from request body."""
        serializer = TaskListSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid input data',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = serializer.validated_data['tasks']
       
        custom_weights = request.data.get('weights')
        weights = None
        if custom_weights:
            weight_serializer = WeightConfigSerializer(data=custom_weights)
            if weight_serializer.is_valid():
                weights = weight_serializer.validated_data
        
        calculator = PriorityCalculator(weights=weights)
        matrix = self._build_matrix(tasks, calculator)
        
        return Response({'matrix': matrix}, status=status.HTTP_200_OK)


class TaskFeedbackView(APIView):
    """
    POST /api/tasks/feedback/ - Submit feedback on task suggestions
    GET /api/tasks/feedback/ - Get feedback statistics
    """
    
    def post(self, request):
        """
        Submit feedback on a task suggestion.
        
        Request body:
        {
            "task_id": 1,
            "was_helpful": true,
            "feedback_notes": "Optional notes"
        }
        """
        task_id = request.data.get('task_id')
        was_helpful = request.data.get('was_helpful')
        feedback_notes = request.data.get('feedback_notes', '')
        
        if task_id is None:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if was_helpful is None:
            return Response(
                {'error': 'was_helpful is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            feedback = TaskFeedback.objects.create(
                task_id=int(task_id),
                was_helpful=bool(was_helpful),
                feedback_notes=str(feedback_notes) if feedback_notes else None
            )
            
            return Response(
                {
                    'message': 'Feedback submitted successfully',
                    'feedback_id': feedback.id
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to save feedback', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get(self, request):
        """Get feedback statistics for learning system."""
        total_feedback = TaskFeedback.objects.count()
        helpful_count = TaskFeedback.objects.filter(was_helpful=True).count()
        not_helpful_count = TaskFeedback.objects.filter(was_helpful=False).count()
        
        helpful_rate = (helpful_count / total_feedback * 100) if total_feedback > 0 else 0
        
        return Response(
            {
                'total_feedback': total_feedback,
                'helpful_count': helpful_count,
                'not_helpful_count': not_helpful_count,
                'helpful_rate': round(helpful_rate, 2)
            },
            status=status.HTTP_200_OK
        )


class LearningAdjustedSuggestView(APIView):
    """
    GET /api/tasks/suggest-learning/ - Get suggestions adjusted based on learning feedback
    POST /api/tasks/suggest-learning/ - Get learning-adjusted suggestions from request body
    """
    
    def _get_adjusted_weights(self):
        """
        Adjust weights based on user feedback.
        If users consistently mark high-importance tasks as helpful, increase importance weight.
        If users mark urgent tasks as helpful, increase urgency weight.
        """
        from django.db import models
        
        feedbacks = TaskFeedback.objects.all()
        if feedbacks.count() < 5:
            return None  
        
     
        helpful_tasks = TaskFeedback.objects.filter(was_helpful=True).values_list('task_id', flat=True)
        not_helpful_tasks = TaskFeedback.objects.filter(was_helpful=False).values_list('task_id', flat=True)
        
        helpful_task_ids = set(helpful_tasks)
        not_helpful_task_ids = set(not_helpful_tasks)
        
      
        helpful_task_objs = Task.objects.filter(pk__in=helpful_task_ids)
        not_helpful_task_objs = Task.objects.filter(pk__in=not_helpful_task_ids)
        
        if helpful_task_objs.count() == 0:
            return None
        
        
        avg_importance_helpful = helpful_task_objs.aggregate(
            avg=models.Avg('importance')
        )['avg'] or 5
        
        avg_importance_not_helpful = not_helpful_task_objs.aggregate(
            avg=models.Avg('importance')
        )['avg'] if not_helpful_task_objs.count() > 0 else 5
        
        
        weights = WEIGHTS.copy()
        
        if avg_importance_helpful > avg_importance_not_helpful + 1:
        
            adjustment = 0.05
            weights['importance'] = min(0.6, weights['importance'] + adjustment)
            weights['urgency'] = max(0.2, weights['urgency'] - adjustment * 0.5)
            weights['effort'] = max(0.05, weights['effort'] - adjustment * 0.25)
            weights['dependencies'] = max(0.05, weights['dependencies'] - adjustment * 0.25)
        elif avg_importance_helpful < avg_importance_not_helpful - 1:
         
            adjustment = 0.05
            weights['effort'] = min(0.4, weights['effort'] + adjustment)
            weights['importance'] = max(0.2, weights['importance'] - adjustment * 0.5)
            weights['urgency'] = max(0.2, weights['urgency'] - adjustment * 0.25)
            weights['dependencies'] = max(0.05, weights['dependencies'] - adjustment * 0.25)
        
     
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def get(self, request):
        """Get learning-adjusted suggestions from database tasks."""
        from django.db import models
        
        tasks = Task.objects.all()
        
        if not tasks.exists():
            return Response(
                {'error': 'No tasks found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task_list = [task.to_dict() for task in tasks]
        
        adjusted_weights = self._get_adjusted_weights()
        weights = adjusted_weights
        
        custom_weights = request.query_params.get('weights')
        if custom_weights:
            try:
                import json
                weights_dict = json.loads(custom_weights)
                weight_serializer = WeightConfigSerializer(data=weights_dict)
                if weight_serializer.is_valid():
                    weights = weight_serializer.validated_data
            except (json.JSONDecodeError, ValueError):
                pass
      
        validator = DependencyValidator()
        is_valid, error_msg = validator.validate_dependencies(task_list)
        if not is_valid:
            return Response(
                {'error': 'Invalid dependencies', 'message': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_cycle, cycle_path = validator.detect_circular_dependencies(task_list)
        if has_cycle:
            return Response(
                {
                    'error': 'Circular dependency detected',
                    'cycle': cycle_path,
                    'message': f"Circular dependency found: {' -> '.join(map(str, cycle_path))}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
        try:
            calculator = PriorityCalculator(weights=weights)
            scored_tasks = calculator.analyze_tasks(task_list)
            
        
            top_tasks = scored_tasks[:3]
            
            suggestions = []
            for task in top_tasks:
                explanation = calculator.generate_task_explanation(task)
                task_dict = {
                    'id': task['id'],
                    'title': task['title'],
                    'due_date': task['due_date'].strftime('%Y-%m-%d') if hasattr(task['due_date'], 'strftime') else task['due_date'],
                    'priority_score': task['priority_score']
                }
                if 'metadata' in task:
                    task_dict['is_overdue'] = task['metadata'].get('is_overdue', False)
                    task_dict['days_overdue'] = task['metadata'].get('days_overdue', 0)
                
                suggestions.append({
                    'task': task_dict,
                    'reason': explanation
                })
            
            response_data = {
                'suggestions': suggestions,
                'weights_used': weights,
                'weights_adjusted': adjusted_weights is not None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Failed to generate suggestions', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Get learning-adjusted suggestions from request body."""
        from django.db import models
        
        serializer = TaskListSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid input data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = serializer.validated_data['tasks']
        
        adjusted_weights = self._get_adjusted_weights()
        weights = adjusted_weights
        
       
        custom_weights = request.data.get('weights')
        if custom_weights:
            weight_serializer = WeightConfigSerializer(data=custom_weights)
            if weight_serializer.is_valid():
                weights = weight_serializer.validated_data
       
        validator = DependencyValidator()
        is_valid, error_msg = validator.validate_dependencies(tasks)
        if not is_valid:
            return Response(
                {'error': 'Invalid dependencies', 'message': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_cycle, cycle_path = validator.detect_circular_dependencies(tasks)
        if has_cycle:
            return Response(
                {
                    'error': 'Circular dependency detected',
                    'cycle': cycle_path,
                    'message': f"Circular dependency found: {' -> '.join(map(str, cycle_path))}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
 
        try:
            calculator = PriorityCalculator(weights=weights)
            scored_tasks = calculator.analyze_tasks(tasks)
            
         
            top_tasks = scored_tasks[:3]
            
    
            suggestions = []
            for task in top_tasks:
                explanation = calculator.generate_task_explanation(task)
                task_dict = {
                    'id': task['id'],
                    'title': task['title'],
                    'due_date': task['due_date'].strftime('%Y-%m-%d') if hasattr(task['due_date'], 'strftime') else task['due_date'],
                    'priority_score': task['priority_score']
                }
                if 'metadata' in task:
                    task_dict['is_overdue'] = task['metadata'].get('is_overdue', False)
                    task_dict['days_overdue'] = task['metadata'].get('days_overdue', 0)
                
                suggestions.append({
                    'task': task_dict,
                    'reason': explanation
                })
            
            response_data = {
                'suggestions': suggestions,
                'weights_used': weights,
                'weights_adjusted': adjusted_weights is not None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Failed to generate suggestions', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


