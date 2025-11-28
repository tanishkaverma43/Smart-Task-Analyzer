"""
Tests for task analyzer functionality.
"""
from django.test import TestCase
from datetime import date, timedelta
from .scoring import PriorityCalculator, WEIGHTS
from .dependency_validator import DependencyValidator


class PriorityCalculatorTestCase(TestCase):
    """Test cases for priority calculation."""
    
    def setUp(self):
        self.calculator = PriorityCalculator()
    
    def test_urgency_overdue_task(self):
        """Test urgency score for overdue tasks."""
        overdue_date = date.today() - timedelta(days=5)
        score = self.calculator.calculate_urgency_score(overdue_date)
        self.assertGreater(score, 80)
    
    def test_urgency_due_today(self):
        """Test urgency score for tasks due today."""
        today = date.today()
        score = self.calculator.calculate_urgency_score(today)
        self.assertEqual(score, 100)
    
    def test_importance_score(self):
        """Test importance scoring."""
        self.assertEqual(self.calculator.calculate_importance_score(10), 100)
        self.assertEqual(self.calculator.calculate_importance_score(5), 50)
        self.assertEqual(self.calculator.calculate_importance_score(1), 10)
    
    def test_effort_quick_wins(self):
        """Test effort scoring rewards quick wins."""
        quick_task_score = self.calculator.calculate_effort_score(1)
        long_task_score = self.calculator.calculate_effort_score(20)
        self.assertGreater(quick_task_score, long_task_score)
    
    def test_dependency_score(self):
        """Test dependency scoring."""
        self.assertEqual(self.calculator.calculate_dependency_score(0), 0)
        self.assertGreater(
            self.calculator.calculate_dependency_score(3),
            self.calculator.calculate_dependency_score(1)
        )
    
    def test_urgency_weekend_consideration(self):
        """Test that urgency calculation considers weekends."""
 
        today = date.today()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7 
        saturday = today + timedelta(days=days_until_saturday)
        
       
        score = self.calculator.calculate_urgency_score(saturday)
       
        self.assertGreater(score, 0)
    
    def test_urgency_holiday_consideration(self):
        """Test that urgency calculation considers holidays."""
        
        new_year = date(date.today().year + 1, 1, 1)
        score = self.calculator.calculate_urgency_score(new_year)
       
        self.assertGreater(score, 0)
    
    def test_working_days_calculation(self):
        """Test working days calculation excludes weekends and holidays."""
        
        start = date.today()
        end = start + timedelta(days=7)
        working_days = PriorityCalculator._count_working_days(start, end)
 
        self.assertLess(working_days, 7)
        self.assertGreater(working_days, 0)
    
    def test_priority_score_calculation(self):
        """Test complete priority score calculation."""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': date.today() + timedelta(days=3),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        
        result = self.calculator.calculate_priority_score(task, dependent_count=0)
        
        self.assertIn('priority_score', result)
        self.assertIn('score_breakdown', result)
        self.assertIn('metadata', result)
        self.assertGreater(result['priority_score'], 0)
        self.assertLessEqual(result['priority_score'], 100)
    
    def test_priority_score_with_dependencies(self):
        """Test priority score increases with dependent count."""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': date.today() + timedelta(days=5),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        score_no_deps = self.calculator.calculate_priority_score(task, dependent_count=0)
        score_with_deps = self.calculator.calculate_priority_score(task, dependent_count=3)
        
        self.assertGreater(score_with_deps['priority_score'], score_no_deps['priority_score'])
    
    def test_analyze_tasks_sorts_by_priority(self):
        """Test that analyze_tasks returns tasks sorted by priority."""
        tasks = [
            {
                'id': 1,
                'title': 'Low Priority',
                'due_date': date.today() + timedelta(days=30),
                'estimated_hours': 10,
                'importance': 2,
                'dependencies': []
            },
            {
                'id': 2,
                'title': 'High Priority',
                'due_date': date.today() + timedelta(days=1),
                'estimated_hours': 2,
                'importance': 9,
                'dependencies': []
            }
        ]
        
        result = self.calculator.analyze_tasks(tasks)
        
        self.assertEqual(len(result), 2)
     
        self.assertEqual(result[0]['id'], 2)
        self.assertGreater(result[0]['priority_score'], result[1]['priority_score'])
    
    def test_custom_weights(self):
        """Test priority calculation with custom weights."""
        custom_weights = {
            'urgency': 0.2,
            'importance': 0.6,
            'effort': 0.1,
            'dependencies': 0.1
        }
        
        calculator = PriorityCalculator(weights=custom_weights)
        
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': date.today() + timedelta(days=10),
            'estimated_hours': 5,
            'importance': 9, 
            'dependencies': []
        }
        
        result = calculator.calculate_priority_score(task, dependent_count=0)
       
        self.assertGreater(result['priority_score'], 50)
    
    def test_invalid_weights_sum(self):
        """Test that invalid weight sums raise ValueError."""
        invalid_weights = {
            'urgency': 0.5,
            'importance': 0.5,
            'effort': 0.5, 
            'dependencies': 0.5
        }
        
        with self.assertRaises(ValueError):
            PriorityCalculator(weights=invalid_weights)
    
    def test_negative_weights(self):
        """Test that negative weights raise ValueError."""
        negative_weights = {
            'urgency': -0.1,
            'importance': 0.3,
            'effort': 0.4,
            'dependencies': 0.4
        }
        
        with self.assertRaises(ValueError):
            PriorityCalculator(weights=negative_weights)
    
    def test_effort_score_ranges(self):
        """Test effort score for various hour ranges."""
      
        self.assertEqual(self.calculator.calculate_effort_score(0.5), 100)

        score_4h = self.calculator.calculate_effort_score(4)
        self.assertGreater(score_4h, 0)
        self.assertLess(score_4h, 100)
        

        score_20h = self.calculator.calculate_effort_score(20)
        self.assertLess(score_20h, score_4h)
    
    def test_urgency_score_ranges(self):
        """Test urgency score for various time ranges."""
        today = date.today()
        
     
        overdue_score = self.calculator.calculate_urgency_score(today - timedelta(days=1))
        self.assertGreater(overdue_score, 80)
        
       
        today_score = self.calculator.calculate_urgency_score(today)
        self.assertEqual(today_score, 100)
        
    
        soon_score = self.calculator.calculate_urgency_score(today + timedelta(days=3))
        self.assertGreater(soon_score, 50)
        self.assertLess(soon_score, 100)
        
     
        later_score = self.calculator.calculate_urgency_score(today + timedelta(days=30))
        self.assertLess(later_score, 50)
    
    def test_importance_score_boundaries(self):
        """Test importance score at boundaries."""
        self.assertEqual(self.calculator.calculate_importance_score(1), 10)
        self.assertEqual(self.calculator.calculate_importance_score(10), 100)
        self.assertEqual(self.calculator.calculate_importance_score(5), 50)
    
    def test_importance_score_clamping(self):
        """Test that importance score clamps invalid values."""
    
        self.assertEqual(self.calculator.calculate_importance_score(0), 10)  # Clamped to 1
        self.assertEqual(self.calculator.calculate_importance_score(15), 100)  # Clamped to 10
    
    def test_dependency_score_scaling(self):
        """Test dependency score scaling with dependent count."""
        scores = [self.calculator.calculate_dependency_score(i) for i in range(6)]
        
       
        for i in range(1, len(scores)):
            self.assertGreaterEqual(scores[i], scores[i-1])
        
        
        self.assertEqual(scores[0], 0)
        
    
        self.assertGreater(scores[2] - scores[1], scores[5] - scores[4])
    
    def test_task_explanation_generation(self):
        """Test task explanation generation."""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': date.today() - timedelta(days=2),
            'estimated_hours': 1,
            'importance': 9,
            'dependencies': []
        }
        
   
        score_data = self.calculator.calculate_priority_score(task, dependent_count=0)
        task.update(score_data)
        
        explanation = self.calculator.generate_task_explanation(task)
        
        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 0)
      
        self.assertIn('overdue', explanation.lower())
    
    def test_analyze_tasks_empty_list(self):
        """Test that analyze_tasks raises error for empty list."""
        with self.assertRaises(ValueError):
            self.calculator.analyze_tasks([])
    
    def test_analyze_tasks_missing_fields(self):
        """Test that analyze_tasks validates required fields."""
        incomplete_task = {
            'id': 1,
            'title': 'Test'
          
        }
        
        with self.assertRaises(ValueError):
            self.calculator.analyze_tasks([incomplete_task])


class DependencyValidatorTestCase(TestCase):
    """Test cases for dependency validation."""
    
    def test_detect_circular_dependency(self):
        """Test circular dependency detection."""
        tasks = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [3]},
            {'id': 3, 'dependencies': [1]} 
        ]
        
        has_cycle, _ = DependencyValidator.detect_circular_dependencies(tasks)
        self.assertTrue(has_cycle)
    
    def test_no_circular_dependency(self):
        """Test valid dependency chain."""
        tasks = [
            {'id': 1, 'dependencies': []},
            {'id': 2, 'dependencies': [1]},
            {'id': 3, 'dependencies': [2]}
        ]
        
        has_cycle, _ = DependencyValidator.detect_circular_dependencies(tasks)
        self.assertFalse(has_cycle)
    
    def test_validate_missing_dependency(self):
        """Test validation catches missing dependencies."""
        tasks = [
            {'id': 1, 'dependencies': [999]}  
        ]
        
        is_valid, _ = DependencyValidator.validate_dependencies(tasks)
        self.assertFalse(is_valid)
    
    def test_count_dependents(self):
        """Test counting dependent tasks."""
        tasks = [
            {'id': 1, 'dependencies': []},
            {'id': 2, 'dependencies': [1]},
            {'id': 3, 'dependencies': [1]}
        ]
        
        counts = DependencyValidator.count_dependents(tasks)
        self.assertEqual(counts[1], 2) 
        self.assertEqual(counts[2], 0)  


