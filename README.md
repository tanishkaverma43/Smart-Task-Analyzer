<div align="center">

# 🎯 Smart Task Analyzer

<div style="font-size: 1.2em; margin: 20px 0; color: #6366f1; animation: fadeIn 2s ease-in;">
An intelligent task prioritization system that uses a sophisticated scoring algorithm to help you focus on what matters most.
</div>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

<div style="animation: slideIn 1s ease-out;">

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Setup Instructions](#-setup-instructions)
- [Algorithm Explanation](#-algorithm-explanation)
- [Design Decisions](#-design-decisions)
- [Time Breakdown](#-time-breakdown)
- [Bonus Challenges](#-bonus-challenges)
- [Future Improvements](#-future-improvements)
- [Features](#-features)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)

</div>

---

## 🎨 Project Overview

<div style="animation: fadeInUp 1s ease-out;">

The **Smart Task Analyzer** is a full-stack web application that intelligently prioritizes tasks based on multiple factors. It helps individuals and teams make data-driven decisions about what to work on next by analyzing urgency, importance, effort, and dependencies.

### Key Capabilities

- ✅ **Multi-Factor Analysis**: Considers urgency, importance, effort, and dependencies
- ✅ **Configurable Strategies**: Four different prioritization approaches
- ✅ **Real-Time Scoring**: Instant priority calculations with detailed breakdowns
- ✅ **Dependency Management**: Detects and prioritizes blocking tasks
- ✅ **Overdue Handling**: Exponential urgency boost for overdue tasks
- ✅ **Beautiful UI**: Modern, responsive interface with smooth animations

</div>

---

## 🚀 Setup Instructions

<div style="animation: fadeInUp 1.2s ease-out;">

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package manager) - Usually comes with Python
- **Web Browser** - Chrome, Firefox, Safari, or Edge (latest versions)

### Step-by-Step Installation

#### 1. Navigate to Project Directory

```bash
cd "path/to/singularium tech"
```

#### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
- `Django==4.2.7` - Web framework
- `djangorestframework==3.14.0` - REST API framework
- `python-dateutil==2.8.2` - Date parsing utilities
- `django-cors-headers==4.3.1` - CORS support for frontend-backend communication

#### 3. Set Up Database

```bash
python manage.py migrate
```

This creates the SQLite database (`db.sqlite3`) with all required tables for storing tasks.

#### 4. Start the Backend Server

```bash
python manage.py runserver
```

The Django API server will start at `http://localhost:8000/`

**Alternative (Windows):**
```bash
start_server.bat
```

#### 5. Launch the Frontend

**Option A: Direct File Open**
- Navigate to the `frontend` folder
- Double-click `index.html` to open in your browser

**Option B: Local Server (Recommended)**
```bash
cd frontend
python -m http.server 8080
```
Then visit `http://localhost:8080` in your browser

### Verify Installation

1. **Check Backend Health:**
   ```bash
   curl http://localhost:8000/api/health/
   ```
   Should return: `{"status": "healthy"}`

2. **Open Frontend:**
   - Navigate to `http://localhost:8080` (or open `index.html` directly)
   - You should see the Smart Task Analyzer interface

### Troubleshooting

**Port Already in Use:**
```bash
# Use a different port
python manage.py runserver 8001
# Then update API_BASE_URL in frontend/app.js
```

**CORS Errors:**
- Ensure `django-cors-headers` is installed: `pip install django-cors-headers`
- Verify `CORS_ALLOW_ALL_ORIGINS = True` in `backend/task_analyzer/settings.py`

**Database Issues:**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

</div>

---

## 🧠 Algorithm Explanation

<div style="animation: fadeInUp 1.4s ease-out;">

The priority scoring algorithm is the heart of the Smart Task Analyzer. It uses a **weighted multi-factor scoring system** that balances competing priorities to determine which tasks should be tackled first. The algorithm calculates a priority score (0-100) for each task by evaluating four key dimensions.

### Core Components

#### 1. Urgency Score (40% Weight)

The urgency component measures how time-sensitive a task is based on its due date. The scoring uses a **non-linear decay function** that heavily penalizes overdue tasks and rewards tasks with approaching deadlines.

- **Overdue Tasks**: Receive an exponential urgency boost (80-100 points). The formula `80 + (days_overdue^1.5) * 2` ensures that tasks become increasingly urgent the longer they're overdue, preventing critical items from being ignored.

- **Due Today**: Maximum urgency score of 100, ensuring same-day deadlines are always top priority.

- **Near-Term Deadlines**: Tasks due within 3 days receive 70-90 points, with linear decay. This creates a sense of urgency for upcoming deadlines without overwhelming the system.

- **Medium-Term**: Tasks due within a week (50-70 points) and two weeks (30-50 points) receive moderate urgency scores.

- **Long-Term**: Tasks further out receive diminishing urgency scores (0-30 points), allowing important but not urgent tasks to still be considered.

#### 2. Importance Score (30% Weight)

Importance is directly mapped from the user's 1-10 rating using a **linear transformation**. A rating of 1 maps to 10 points, while a rating of 10 maps to 100 points. This ensures that user judgment about task importance is preserved proportionally in the final score.

The 30% weight means that even highly important tasks (9-10 rating) won't automatically dominate unless they're also somewhat urgent or have other favorable factors. This prevents the "important but not urgent" quadrant from completely taking over the priority list.

#### 3. Effort Score (15% Weight)

The effort component rewards **"quick wins"** - tasks that can be completed quickly. This is based on psychological research showing that completing small tasks provides momentum and reduces cognitive load.

- Tasks under 1 hour receive 100 points
- 1-2 hours: 90 points
- 2-4 hours: 70 points
- 4-8 hours: 50 points
- 8-16 hours: 30 points
- Over 16 hours: 10 points (with further decay)

This creates a preference for tasks that can be knocked out quickly, helping users build momentum while still considering other factors.

#### 4. Dependency Score (15% Weight)

The dependency component identifies **blocking tasks** - tasks that prevent other tasks from being started. This is crucial for project management, as completing blocking tasks unlocks multiple downstream tasks.

- 0 dependents: 0 points (no blocking impact)
- 1 dependent: 30 points
- 2 dependents: 50 points
- 3 dependents: 65 points
- 4 dependents: 75 points
- 5+ dependents: 80-100 points (with diminishing returns)

The algorithm counts how many tasks list this task in their dependencies array, creating a network-aware prioritization system.

### Weighted Combination

The final priority score is calculated as:

```
Priority Score = (Urgency × 0.40) + (Importance × 0.30) + (Effort × 0.15) + (Dependencies × 0.15)
```

This weighted sum ensures that:
- **Urgent tasks** (especially overdue ones) are prioritized
- **Important tasks** still rank highly even if not urgent
- **Quick wins** get a boost to help build momentum
- **Blocking tasks** are elevated to unblock the workflow

### Handling Edge Cases

The algorithm includes several sophisticated edge case handlers:

1. **Overdue Task Escalation**: Overdue tasks receive exponential urgency increases, ensuring they don't get buried even if they have low importance.

2. **Circular Dependency Detection**: The system validates dependencies to prevent circular references that would create impossible task sequences.

3. **Missing Data Validation**: All required fields are validated before scoring, with clear error messages for invalid inputs.

4. **Configurable Weights**: The default 40-30-15-15 distribution can be customized for different use cases (e.g., deadline-driven projects might use 70% urgency, while strategic planning might emphasize importance).

### Example Calculation

Consider a task that is:
- **2 days overdue** (urgency: 95)
- **Importance rating: 8** (importance: 80)
- **Estimated 2 hours** (effort: 90)
- **Blocks 2 other tasks** (dependencies: 50)

**Calculation:**
```
Priority = (95 × 0.40) + (80 × 0.30) + (90 × 0.15) + (50 × 0.15)
         = 38.0 + 24.0 + 13.5 + 7.5
         = 83.0
```

This task would rank very highly due to being overdue, important, quick to complete, and blocking other work.

</div>

---

## 🎯 Design Decisions

<div style="animation: fadeInUp 1.6s ease-out;">

Throughout the development of Smart Task Analyzer, several key design decisions were made to balance functionality, performance, and user experience. Here are the most significant trade-offs:

### 1. SQLite vs. PostgreSQL/MySQL

**Decision**: Use SQLite for the database

**Rationale**: 
- **Pros**: Zero configuration, perfect for development and small-scale deployments, file-based (easy to backup), sufficient for the task management use case
- **Cons**: Limited concurrent write performance, not ideal for high-traffic production

**Trade-off**: Chose simplicity and ease of setup over scalability. For production, migration to PostgreSQL would be straightforward.

### 2. Vanilla JavaScript vs. Framework

**Decision**: Use vanilla JavaScript instead of React/Vue/Angular

**Rationale**:
- **Pros**: No build step required, faster development for simple UI, smaller bundle size, easier to understand for beginners
- **Cons**: More manual DOM manipulation, no component reusability, harder to scale for complex features

**Trade-off**: Prioritized simplicity and quick iteration over long-term maintainability. For a larger application, a framework would be beneficial.

### 3. Weighted Scoring vs. Rule-Based System

**Decision**: Implement weighted multi-factor scoring instead of if-then rules

**Rationale**:
- **Pros**: More flexible, handles edge cases gracefully, allows fine-tuning through weights, mathematically sound
- **Cons**: Less intuitive to understand, requires tuning weights, can produce unexpected results

**Trade-off**: Chose mathematical rigor over simplicity. The weighted approach allows for more nuanced prioritization but requires users to understand the scoring system.

### 4. Exponential vs. Linear Urgency for Overdue Tasks

**Decision**: Use exponential urgency increase for overdue tasks

**Rationale**:
- **Pros**: Prevents overdue tasks from being ignored, creates strong incentive to complete them, matches real-world urgency perception
- **Cons**: Can cause overdue tasks to dominate the list, might hide important non-overdue tasks

**Trade-off**: Prioritized preventing task abandonment over balanced visibility. The exponential curve ensures overdue items are addressed quickly.

### 5. Frontend-Backend Separation

**Decision**: Separate frontend (static HTML) from backend (Django API)

**Rationale**:
- **Pros**: Can serve frontend from CDN, backend can be scaled independently, clear separation of concerns, easier to test
- **Cons**: Requires CORS configuration, more complex deployment, two servers to manage

**Trade-off**: Chose architectural flexibility over deployment simplicity. This separation allows for future mobile apps or different frontend frameworks.

### 6. Real-Time Scoring vs. Cached Scores

**Decision**: Calculate scores on-demand rather than storing pre-calculated scores

**Rationale**:
- **Pros**: Always up-to-date (scores change as dates approach), no cache invalidation complexity, simpler data model
- **Cons**: More CPU usage, slightly slower response times for large task lists

**Trade-off**: Prioritized accuracy and simplicity over performance. For 100+ tasks, caching might be beneficial, but for typical use cases (<50 tasks), real-time calculation is sufficient.

### 7. Single Strategy vs. Multiple Strategies

**Decision**: Implement four different sorting strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven)

**Rationale**:
- **Pros**: Users can adapt to different scenarios, demonstrates algorithm flexibility, provides learning value
- **Cons**: More code to maintain, potential user confusion about which to use

**Trade-off**: Chose flexibility and educational value over simplicity. The multiple strategies showcase the algorithm's configurability.

### 8. JSON Bulk Import vs. CSV/Excel

**Decision**: Support JSON bulk import instead of CSV/Excel

**Rationale**:
- **Pros**: JSON is structured, supports nested data (dependencies), easy to parse, no external libraries needed
- **Cons**: Less user-friendly than CSV, requires technical knowledge

**Trade-off**: Prioritized developer-friendly format over end-user convenience. Future versions could add CSV support.

</div>

---

## ⏱️ Time Breakdown

<div style="animation: fadeInUp 1.8s ease-out;">

Here's an approximate breakdown of time spent on each section of the project:

### Backend Development (~40 hours)

| Component | Time | Description |
|-----------|------|-------------|
| **Project Setup** | 2 hours | Django project initialization, virtual environment, dependencies |
| **Data Models** | 4 hours | Task model design, database schema, migrations, field validation |
| **Priority Algorithm** | 12 hours | Core scoring logic, urgency/importance/effort/dependency calculations, edge case handling, testing |
| **API Endpoints** | 6 hours | REST API design, serializers, request/response handling, error responses |
| **Dependency Validation** | 3 hours | Circular dependency detection, dependency counting, validation logic |
| **Testing** | 5 hours | Unit tests, integration tests, edge case testing, test automation |
| **Documentation** | 3 hours | Code comments, API documentation, inline documentation |
| **Bug Fixes & Refinement** | 5 hours | Debugging, performance optimization, code cleanup |

### Frontend Development (~25 hours)

| Component | Time | Description |
|-----------|------|-------------|
| **HTML Structure** | 3 hours | Semantic HTML, form design, layout structure, accessibility |
| **CSS Styling** | 6 hours | Responsive design, color scheme, animations, mobile optimization |
| **JavaScript Logic** | 8 hours | API integration, form handling, task management, strategy switching, error handling |
| **UI/UX Polish** | 4 hours | Loading states, error messages, visual feedback, animations |
| **Testing & Debugging** | 3 hours | Cross-browser testing, CORS issues, API integration testing |
| **Documentation** | 1 hour | Frontend README, usage instructions |

### Integration & Testing (~8 hours)

| Component | Time | Description |
|-----------|------|-------------|
| **CORS Configuration** | 1 hour | Setting up django-cors-headers, testing cross-origin requests |
| **End-to-End Testing** | 3 hours | Full workflow testing, edge cases, user scenarios |
| **Performance Testing** | 2 hours | Large task list handling, response time optimization |
| **Bug Fixes** | 2 hours | Integration issues, data flow problems |

### Documentation & Polish (~7 hours)

| Component | Time | Description |
|-----------|------|-------------|
| **Main README** | 3 hours | Comprehensive documentation, setup instructions, examples |
| **Code Comments** | 2 hours | Inline documentation, docstrings, type hints |
| **Example Data** | 1 hour | Creating sample tasks, test scenarios |
| **Final Review** | 1 hour | Proofreading, formatting, consistency checks |

### **Total Estimated Time: ~80 hours**

*Note: These estimates assume a developer familiar with Django and JavaScript. Actual time may vary based on experience level and specific requirements.*

</div>

---

## 🏆 Bonus Challenges

<div style="animation: fadeInUp 2s ease-out;">

Several bonus features and challenges were implemented beyond the core requirements:

### ✅ Implemented Bonus Features

1. **Multiple Sorting Strategies** ⭐
   - Implemented four different prioritization strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven)
   - Allows users to adapt the algorithm to different scenarios
   - Demonstrates the flexibility of the weighted scoring system

2. **Comprehensive Error Handling** ⭐
   - Detailed validation error messages
   - Graceful handling of missing/invalid data
   - User-friendly error display in the frontend

3. **Top 3 Recommendations with Explanations** ⭐
   - AI-generated explanations for why tasks are prioritized
   - Human-readable reasoning (e.g., "overdue by 3 days, high importance")
   - Helps users understand the algorithm's decisions

4. **Responsive Design** ⭐
   - Mobile-first approach
   - Works seamlessly on desktop, tablet, and mobile devices
   - Touch-friendly interface elements

5. **Visual Priority Indicators** ⭐
   - Color-coded priority levels (Critical/High/Medium/Low)
   - Score breakdown visualization
   - Visual indicators for overdue tasks

6. **Bulk Task Import** ⭐
   - JSON bulk import functionality
   - Example data loader for quick testing
   - Supports complex dependency structures

7. **Real-Time Form Validation** ⭐
   - Client-side validation before submission
   - Clear error messages for invalid inputs
   - Prevents invalid data from reaching the API

8. **Loading States & Animations** ⭐
   - Smooth loading indicators during API calls
   - Animated transitions for task list updates
   - Professional user experience polish

9. **Statistics Dashboard** ⭐
   - Total task count
   - High priority task count
   - Average priority score
   - Quick overview of task list health

10. **Dependency Visualization** ⭐
    - Clear indication of which tasks block others
    - Dependency count in score breakdown
    - Helps identify critical path tasks

### 🎯 Additional Considerations

- **Circular Dependency Detection**: Prevents impossible task sequences
- **Overdue Task Escalation**: Exponential urgency boost for overdue items
- **Configurable Algorithm Weights**: Allows customization of prioritization factors
- **Comprehensive Test Suite**: Automated testing for all major features
- **Clean Code Architecture**: Well-organized, maintainable codebase

</div>

---

## 🔮 Future Improvements

<div style="animation: fadeInUp 2.2s ease-out;">

With more time and resources, here are the improvements and features that would enhance the Smart Task Analyzer:

### Short-Term Enhancements (1-2 weeks)

1. **User Authentication & Multi-User Support**
   - User accounts and login system
   - Personal task lists per user
   - Team collaboration features
   - Shared task boards

2. **Task Persistence & History**
   - Save task lists to database
   - Task completion tracking
   - Historical priority changes
   - Task archive functionality

3. **Export & Import Features**
   - Export tasks to CSV/Excel
   - Import from popular task managers (Todoist, Asana, Trello)
   - PDF reports with prioritized task lists
   - Calendar integration (iCal export)

4. **Advanced Filtering & Search**
   - Filter by priority level, due date range, importance
   - Full-text search across task titles
   - Tag/category system
   - Custom views and saved filters

5. **Enhanced UI Features**
   - Dark mode theme
   - Drag-and-drop task reordering
   - Task editing inline
   - Keyboard shortcuts for power users

### Medium-Term Enhancements (1-2 months)

6. **Machine Learning Integration**
   - Learn from user completion patterns
   - Predict task duration based on history
   - Auto-adjust importance ratings
   - Personalized priority recommendations

7. **Advanced Analytics**
   - Task completion rate tracking
   - Time spent vs. estimated analysis
   - Priority accuracy metrics
   - Productivity insights dashboard

8. **Collaboration Features**
   - Task assignment to team members
   - Comments and notes on tasks
   - Activity feed
   - Notification system

9. **Mobile Applications**
   - Native iOS app
   - Native Android app
   - Offline mode support
   - Push notifications for deadlines

10. **Integration with External Tools**
    - GitHub issue integration
    - Jira synchronization
    - Slack notifications
    - Email reminders

### Long-Term Enhancements (3-6 months)

11. **Advanced Algorithm Features**
    - Context-aware prioritization (time of day, energy levels)
    - Multi-objective optimization (balance multiple goals)
    - Dependency graph visualization
    - Critical path analysis

12. **Enterprise Features**
    - Role-based access control
    - Department/project organization
    - Custom workflow automation
    - Advanced reporting and analytics

13. **AI-Powered Features**
    - Natural language task creation
    - Automatic task breakdown
    - Smart deadline suggestions
    - Proactive deadline warnings

14. **Performance Optimizations**
    - Caching layer for frequently accessed tasks
    - Database query optimization
    - Real-time updates via WebSockets
    - Horizontal scaling support

15. **Accessibility Improvements**
    - Screen reader optimization
    - Keyboard navigation enhancements
    - High contrast mode
    - Internationalization (i18n)

### Technical Debt & Refactoring

- **Migrate to React/Vue**: For better maintainability and component reusability
- **PostgreSQL Migration**: For production scalability
- **API Versioning**: Support multiple API versions
- **Comprehensive Test Coverage**: Increase test coverage to 90%+
- **CI/CD Pipeline**: Automated testing and deployment
- **Docker Containerization**: Easy deployment and environment consistency
- **API Rate Limiting**: Prevent abuse and ensure fair usage
- **Comprehensive Logging**: Better debugging and monitoring

### Research & Experimentation

- **A/B Testing Framework**: Test different algorithm weights
- **User Behavior Analytics**: Understand how users interact with the system
- **Gamification Elements**: Points, streaks, achievements to increase engagement
- **Time Blocking Integration**: Suggest optimal time slots for tasks

</div>

---

## ✨ Features

<div style="animation: fadeInUp 2.4s ease-out;">

### Backend (Django + Python)

✅ **Task Model with SQLite Database**
- Auto-incrementing task IDs
- All required fields: title, due_date, estimated_hours, importance, dependencies
- Timestamp tracking (created_at, updated_at)
- Data validation with validators
- Indexed fields for performance

✅ **Intelligent Priority Algorithm**
- Configurable weight system (40% urgency, 30% importance, 15% effort, 15% dependencies)
- Handles overdue tasks with exponential urgency scoring
- Rewards "quick wins" (low-effort tasks)
- Prioritizes tasks that block others
- Generates human-readable explanations

✅ **Required API Endpoints**
- `POST /api/tasks/analyze/` - Analyze and sort tasks by priority
- `GET /api/tasks/suggest/` - Get top 3 task recommendations with explanations

✅ **Additional CRUD Endpoints**
- `GET /api/tasks/` - List all tasks from database
- `POST /api/tasks/` - Create a single task
- `GET /api/tasks/<id>/` - Retrieve a specific task
- `PUT /api/tasks/<id>/` - Update a task
- `DELETE /api/tasks/<id>/` - Delete a task
- `POST /api/tasks/bulk/` - Bulk create tasks
- `DELETE /api/tasks/clear/` - Clear all tasks
- `GET /api/health/` - Health check endpoint

### Frontend (HTML/CSS/JavaScript)

✅ **Input Section**
- Form to add individual tasks (ID auto-increments)
- Bulk JSON input for multiple tasks
- "Analyze Tasks" button with loading states
- Real-time form validation

✅ **Output Section**
- Sorted tasks with calculated priority scores
- Color-coded priority indicators (Critical/High/Medium/Low)
- Score breakdowns showing each factor's contribution
- Task details (title, due date, effort, importance)
- Visual indicators for overdue tasks

✅ **Sorting Strategies**
- **Smart Balance** (Recommended): Balances all factors
- **Fastest Wins**: Prioritizes low-effort tasks
- **High Impact**: Prioritizes importance over everything
- **Deadline Driven**: Prioritizes by due date

✅ **UI Features**
- Responsive design (works on all screen sizes)
- Error handling with user-friendly messages
- Loading states during API calls
- Success/error toast notifications
- Clean, modern interface with smooth animations

</div>

---

## 📖 Usage Guide

<div style="animation: fadeInUp 2.6s ease-out;">

### Adding Tasks

**Method 1: Single Task Form**
1. Click on the "Single Task" tab
2. Fill in the task details:
   - Title: Task name/description
   - Due Date: When the task is due
   - Hours: Estimated time to complete
   - Importance: Rating from 1-10
   - Dependencies: Comma-separated task IDs (optional)
3. Click "Add Task"

**Method 2: Bulk JSON Input**
1. Click on the "Bulk JSON" tab
2. Paste your JSON data in the format:
```json
{
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ]
}
```
3. Click "Load Tasks from JSON"
4. Or click "Load Example Data" to see sample tasks

### Analyzing Tasks

1. Add at least one task
2. Select a sorting strategy from the dropdown:
   - **Smart Balance** - Recommended for most cases
   - **Fastest Wins** - When you want quick wins
   - **High Impact** - For high-priority work
   - **Deadline Driven** - When deadlines are critical
3. Click "Analyze Tasks"
4. View the prioritized list with:
   - Priority rankings (#1, #2, #3, etc.)
   - Priority scores and levels
   - Score breakdowns
   - Due date status
   - Top 3 recommendations with explanations

### Example Use Cases

**Scenario 1: Sprint Planning**
- Add all sprint tasks with realistic effort estimates
- Use "Smart Balance" to get optimal task order
- Check "Top 3 Recommendations" for what to tackle first

**Scenario 2: Urgent Bug Fixes**
- Add bugs with overdue or near-due dates
- Use "Deadline Driven" to sort by urgency
- The algorithm will automatically prioritize overdue items

**Scenario 3: Technical Debt**
- Add tech debt items with low importance but high effort
- Use "Fastest Wins" to knock out quick improvements
- Balance with "High Impact" for critical refactors

</div>

---

## 📁 Project Structure

<div style="animation: fadeInUp 2.8s ease-out;">

```
singularium tech/
├── frontend/
│   ├── index.html          # Main UI
│   ├── app.js              # Frontend logic
│   ├── styles.css          # Styling
│   └── README.md           # Frontend docs
│
├── backend/
│   ├── manage.py           # Django management
│   ├── requirements.txt    # Python dependencies
│   ├── start_server.bat    # Windows startup script
│   ├── task_analyzer/      # Django project settings
│   │   ├── settings.py     # Project settings
│   │   └── urls.py         # Main URL config
│   └── tasks/              # Django app
│       ├── models.py       # Task model
│       ├── views.py        # API endpoints
│       ├── serializers.py  # Data validation
│       ├── urls.py         # URL routing
│       ├── scoring.py      # Priority algorithm
│       └── dependency_validator.py  # Dependency checks
│
├── db.sqlite3              # SQLite database
├── requirements.txt        # Root dependencies
├── test_automated.py       # Test suite
├── example_tasks.json      # Sample data
└── README.md               # This file
```

</div>

---

## 📊 API Documentation

<div style="animation: fadeInUp 3s ease-out;">

### POST /api/tasks/analyze/

Analyzes and prioritizes a list of tasks.

**Request:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ]
}
```

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": [],
      "priority_score": 85.5,
      "score_breakdown": {
        "urgency_score": 40.0,
        "importance_score": 24.0,
        "effort_score": 10.5,
        "dependency_score": 11.0
      }
    }
  ]
}
```

### GET /api/tasks/suggest/

Returns top 3 task recommendations with explanations.

**Response:**
```json
{
  "suggestions": [
    {
      "task": {
        "id": 1,
        "title": "Fix bug",
        "due_date": "2025-11-30",
        "priority_score": 85.5
      },
      "reason": "This task is due in 3 day(s), high importance (8/10)."
    }
  ]
}
```

</div>

---

## 🧪 Testing

<div style="animation: fadeInUp 3.2s ease-out;">

A comprehensive test suite is included to verify all requirements:

```bash
python test_automated.py
```

This tests:
- ✓ Health check endpoint
- ✓ Database operations (CRUD)
- ✓ Task creation (single and bulk)
- ✓ Priority algorithm
- ✓ POST /api/tasks/analyze/ endpoint
- ✓ GET /api/tasks/suggest/ endpoint
- ✓ Overdue task handling
- ✓ Circular dependency detection
- ✓ Invalid data handling
- ✓ SQLite persistence

</div>

---

## 🐛 Troubleshooting

<div style="animation: fadeInUp 3.4s ease-out;">

**Server won't start:**
- Check if port 8000 is already in use
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.8+)

**Database errors:**
- Delete `db.sqlite3` and run `python manage.py migrate` again
- Check migrations: `python manage.py showmigrations`

**CORS errors:**
- Verify `django-cors-headers` is installed
- Check `CORS_ALLOW_ALL_ORIGINS` in settings.py

**Tests failing:**
- Ensure Django server is running
- Check if the correct port (8000) is being used
- Verify database has been created and migrated

</div>

---

<div align="center" style="margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; animation: fadeIn 3.6s ease-out;">

## 🎉 Thank You!

**Built with Django 4.2.7, Django REST Framework, and Vanilla JavaScript**

*Last Updated: November 27, 2025*

<div style="margin-top: 20px; font-size: 0.9em; opacity: 0.9;">
Happy task prioritizing! 🎯
</div>

</div>

<style>
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Table styling */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
}

table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
}

table td {
    padding: 12px;
    border-bottom: 1px solid #e0e0e0;
}

table tr:hover {
    background-color: #f5f5f5;
    transition: background-color 0.2s ease;
}

/* Code block styling */
pre {
    background: #f4f4f4;
    border-left: 4px solid #667eea;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}

/* Link hover effects */
a {
    color: #667eea;
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover {
    color: #764ba2;
    text-decoration: underline;
}

/* Badge animations */
img[src*="badge"] {
    transition: transform 0.2s ease;
}

img[src*="badge"]:hover {
    transform: scale(1.1);
}
</style>
