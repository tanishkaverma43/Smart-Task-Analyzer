<div align="center" style="animation: fadeIn 1s ease-out;">

# 🎯 Smart Task Analyzer

<div style="font-size: 1.2em; margin: 20px 0; color: #6366f1; animation: fadeInUp 1.2s ease-out;">
An intelligent task prioritization system that uses a sophisticated scoring algorithm to help you focus on what matters most.
</div>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

<div style="animation: slideIn 1s ease-out;">

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Features](#-features)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)

</div>

---

<div style="animation: fadeInUp 1.4s ease-out;">

## 🎨 Overview

The **Smart Task Analyzer** is a full-stack web application that intelligently prioritizes tasks based on urgency, importance, effort, and dependencies. It helps individuals and teams make data-driven decisions about what to work on next.

### Key Capabilities

- ✅ Multi-factor analysis (urgency, importance, effort, dependencies)
- ✅ Configurable prioritization strategies
- ✅ Real-time scoring with detailed breakdowns
- ✅ Dependency management and blocking task detection
- ✅ Modern, responsive UI

</div>

---

<div style="animation: fadeInUp 1.6s ease-out;">

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Set up database:**
   ```bash
   cd backend
   python manage.py migrate
   ```

3. **Start backend server:**
   ```bash
   python manage.py runserver
   ```
   Server runs at `http://localhost:8000/`

4. **Launch frontend:**
   - Open `frontend/index.html` in your browser, or
   - Run: `cd frontend && python -m http.server 8080`

</div>

---

<div style="animation: fadeInUp 1.8s ease-out;">

## ✨ Features

### Backend
- Task model with SQLite database
- Intelligent priority algorithm (weighted scoring)
- REST API endpoints for task management
- Dependency validation and circular dependency detection

### Frontend
- Single task and bulk JSON input
- Multiple sorting strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven)
- Real-time priority scoring with visual indicators
- Responsive design

</div>

---

<div style="animation: fadeInUp 2s ease-out;">

## 📖 Usage

### Adding Tasks

**Single Task:**
1. Fill in task details (title, due date, hours, importance, dependencies)
2. Click "Add Task"

**Bulk Import:**
1. Paste JSON data in the format:
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
2. Click "Load Tasks from JSON"

### Analyzing Tasks

1. Add tasks
2. Select a sorting strategy
3. Click "Analyze Tasks"
4. View prioritized list with scores and recommendations

</div>

---

<div style="animation: fadeInUp 2.2s ease-out;">

## 📊 API Documentation

### POST /api/tasks/analyze/

Analyzes and prioritizes tasks.

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

### Other Endpoints

- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create a task
- `GET /api/tasks/<id>/` - Get specific task
- `PUT /api/tasks/<id>/` - Update task
- `DELETE /api/tasks/<id>/` - Delete task
- `POST /api/tasks/bulk/` - Bulk create
- `GET /api/health/` - Health check

</div>

---

<div style="animation: fadeInUp 2.4s ease-out;">

## 📁 Project Structure

```
singularium tech/
├── frontend/
│   ├── index.html          # Main UI
│   ├── app.js              # Frontend logic
│   └── styles.css          # Styling
│
├── backend/
│   ├── manage.py           # Django management
│   ├── requirements.txt    # Python dependencies
│   ├── task_analyzer/      # Django project settings
│   └── tasks/              # Django app
│       ├── models.py       # Task model
│       ├── views.py        # API endpoints
│       ├── serializers.py  # Data validation
│       ├── urls.py         # URL routing
│       └── scoring.py      # Priority algorithm
│
└── db.sqlite3              # SQLite database
```

</div>

---

<div style="animation: fadeInUp 2.6s ease-out;">

## 🧪 Testing

Run the test suite:

```bash
python test_automated.py
```

</div>

---

<div style="animation: fadeInUp 2.8s ease-out;">

## 🐛 Troubleshooting

**Port already in use:**
```bash
python manage.py runserver 8001
```

**CORS errors:**
- Ensure `django-cors-headers` is installed
- Verify `CORS_ALLOW_ALL_ORIGINS = True` in settings.py

**Database issues:**
```bash
rm db.sqlite3
python manage.py migrate
```

</div>

---

<div align="center" style="margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; animation: fadeIn 3s ease-out;">

## 🎉 Thank You!

**Built with Django 4.2.7, Django REST Framework, and Vanilla JavaScript**

<div style="margin-top: 20px; font-size: 0.9em; opacity: 0.9;">
Happy task prioritizing! 🎯
</div>

</div>
