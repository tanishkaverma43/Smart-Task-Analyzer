"""
URL routing for task analyzer API.
"""
from django.urls import path
from .views import (
    AnalyzeTasksView,
    SuggestTasksView,
    HealthCheckView,
    TaskListCreateView,
    TaskDetailView,
    TaskBulkCreateView,
    TaskClearAllView,
    AnalyzeStoredTasksView,
    WeightConfigView,
    DependencyGraphView,
    EisenhowerMatrixView,
    TaskFeedbackView,
    LearningAdjustedSuggestView
)

urlpatterns = [
   
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    
    path('tasks/analyze/', AnalyzeTasksView.as_view(), name='analyze-tasks'),
    path('tasks/suggest/', SuggestTasksView.as_view(), name='suggest-tasks'),
    path('tasks/weights/', WeightConfigView.as_view(), name='weight-config'),
    path('tasks/bulk/', TaskBulkCreateView.as_view(), name='task-bulk-create'),
    path('tasks/clear/', TaskClearAllView.as_view(), name='task-clear-all'),
    path('tasks/analyze-stored/', AnalyzeStoredTasksView.as_view(), name='analyze-stored-tasks'),
    path('tasks/dependency-graph/', DependencyGraphView.as_view(), name='dependency-graph'),
    path('tasks/eisenhower-matrix/', EisenhowerMatrixView.as_view(), name='eisenhower-matrix'),
    path('tasks/feedback/', TaskFeedbackView.as_view(), name='task-feedback'),
    path('tasks/suggest-learning/', LearningAdjustedSuggestView.as_view(), name='suggest-learning'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    
   
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
]


