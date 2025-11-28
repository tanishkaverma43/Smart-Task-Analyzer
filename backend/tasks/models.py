"""
Task models for the task analyzer application.
Tasks are persisted to SQLite database.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Task(models.Model):
    """
    Task model for storing task information in SQLite database.
    
    Each task has:
    - title: Task name/description
    - due_date: When the task is due
    - estimated_hours: Effort required
    - importance: User priority rating (1-10)
    - dependencies: JSON field storing list of dependent task IDs
    - created_at: Timestamp when task was created
    - updated_at: Timestamp when task was last updated
    """
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Estimated hours to complete the task"
    )
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Task importance on scale of 1-10"
    )
    dependencies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task IDs this task depends on"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['due_date']),
            models.Index(fields=['importance']),
        ]
    
    def __str__(self):
        return f"{self.pk}. {self.title}"
    
    def to_dict(self):
        """Convert task to dictionary for API responses."""
        from datetime import date
        due_date_str = self.due_date if isinstance(self.due_date, str) else self.due_date.strftime('%Y-%m-%d')
        return {
            'id': self.pk,
            'title': self.title,
            'due_date': due_date_str,
            'estimated_hours': float(self.estimated_hours),
            'importance': self.importance,
            'dependencies': self.dependencies if self.dependencies else []
        }


class TaskFeedback(models.Model):
    """
    Model to store user feedback on task suggestions for learning system.
    """
    task_id = models.IntegerField(help_text="ID of the task that was suggested")
    was_helpful = models.BooleanField(help_text="Whether the suggestion was helpful")
    feedback_notes = models.TextField(blank=True, null=True, help_text="Optional feedback notes")
    suggested_at = models.DateTimeField(auto_now_add=True, help_text="When the suggestion was made")
    feedback_at = models.DateTimeField(auto_now=True, help_text="When feedback was provided")
    
    class Meta:
        app_label = 'tasks'
        ordering = ['-feedback_at']
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['was_helpful']),
        ]
    
    def __str__(self):
        return f"Feedback for Task {self.task_id}: {'Helpful' if self.was_helpful else 'Not Helpful'}"
