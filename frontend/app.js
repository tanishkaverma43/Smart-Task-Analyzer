
let tasks = [];
let currentStrategy = 'smart';
const API_BASE_URL = 'http://localhost:8000/api';


const strategyDescriptions = {
    smart: 'Balances urgency, importance, effort, and dependencies for optimal prioritization',
    fastest: 'Prioritizes low-effort tasks for quick wins and momentum',
    impact: 'Prioritizes importance over everything else - focuses on high-value tasks',
    deadline: 'Prioritizes based on due date - urgent deadlines come first'
};


const strategyWeights = {
    smart: { urgency: 0.40, importance: 0.30, effort: 0.15, dependencies: 0.15 },
    fastest: { urgency: 0.15, importance: 0.15, effort: 0.60, dependencies: 0.10 },
    impact: { urgency: 0.15, importance: 0.60, effort: 0.10, dependencies: 0.15 },
    deadline: { urgency: 0.70, importance: 0.15, effort: 0.05, dependencies: 0.10 }
};


const elements = {

    taskForm: document.getElementById('taskForm'),
    taskTitle: document.getElementById('taskTitle'),
    dueDate: document.getElementById('dueDate'),
    estimatedHours: document.getElementById('estimatedHours'),
    importance: document.getElementById('importance'),
    importanceValue: document.getElementById('importanceValue'),
    dependencies: document.getElementById('dependencies'),
    

    tabButtons: document.querySelectorAll('.tab-button'),
    formTab: document.getElementById('formTab'),
    bulkTab: document.getElementById('bulkTab'),
   
    taskList: document.getElementById('taskList'),
    taskCount: document.getElementById('taskCount'),
    clearTasks: document.getElementById('clearTasks'),
 
    jsonInput: document.getElementById('jsonInput'),
    loadJson: document.getElementById('loadJson'),
    loadExample: document.getElementById('loadExample'),
    
  
    analyzeBtn: document.getElementById('analyzeBtn'),
    sortingStrategy: document.getElementById('sortingStrategy'),
    strategyDescription: document.getElementById('strategyDescription'),
    
  
    loadingState: document.getElementById('loadingState'),
    errorState: document.getElementById('errorState'),
    errorMessage: document.getElementById('errorMessage'),
    emptyState: document.getElementById('emptyState'),
    results: document.getElementById('results'),
    taskResults: document.getElementById('taskResults'),
    suggestions: document.getElementById('suggestions'),
    suggestionsList: document.getElementById('suggestionsList'),
    strategyIndicator: document.getElementById('strategyIndicator'),
    activeStrategyName: document.getElementById('activeStrategyName'),
    
   
    totalTasks: document.getElementById('totalTasks'),
    highPriority: document.getElementById('highPriority'),
    avgScore: document.getElementById('avgScore'),
    
   
    retryBtn: document.getElementById('retryBtn'),
    
  
    dependencyGraph: document.getElementById('dependencyGraph'),
    graphContainer: document.getElementById('graphContainer'),
    cycleWarning: document.getElementById('cycleWarning'),
    eisenhowerMatrix: document.getElementById('eisenhowerMatrix'),
    toggleGraph: document.getElementById('toggleGraph'),
    toggleMatrix: document.getElementById('toggleMatrix')
};


document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    initializeStrategy();
    setDefaultDueDate();
    loadTasksFromDatabase();
});

function initializeStrategy() {
   
    if (elements.sortingStrategy && elements.strategyDescription) {
        const initialStrategy = elements.sortingStrategy.value || 'smart';
        currentStrategy = initialStrategy;
        elements.strategyDescription.textContent = strategyDescriptions[currentStrategy] || strategyDescriptions.smart;
    }
}

function initializeEventListeners() {
    
    elements.taskForm.addEventListener('submit', handleTaskSubmit);
    
    elements.importance.addEventListener('input', (e) => {
        elements.importanceValue.textContent = e.target.value;
    });
    
    elements.tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });
    

    elements.loadJson.addEventListener('click', handleLoadJson);
    elements.loadExample.addEventListener('click', loadExampleData);
    
   
    elements.analyzeBtn.addEventListener('click', analyzeTasks);
    elements.sortingStrategy.addEventListener('change', handleStrategyChange);
    
    
    elements.clearTasks.addEventListener('click', clearAllTasks);
    
    elements.retryBtn.addEventListener('click', analyzeTasks);
    
    if (elements.toggleGraph) {
        elements.toggleGraph.addEventListener('click', () => {
            if (elements.dependencyGraph) {
                elements.dependencyGraph.style.display = 
                    elements.dependencyGraph.style.display === 'none' ? 'block' : 'none';
            }
        });
    }
    
    if (elements.toggleMatrix) {
        elements.toggleMatrix.addEventListener('click', () => {
            if (elements.eisenhowerMatrix) {
                elements.eisenhowerMatrix.style.display = 
                    elements.eisenhowerMatrix.style.display === 'none' ? 'block' : 'none';
            }
        });
    }
}


function switchTab(tabName) {
    
    elements.tabButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    elements.formTab.classList.toggle('active', tabName === 'form');
    elements.bulkTab.classList.toggle('active', tabName === 'bulk');
}

function setDefaultDueDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    elements.dueDate.value = tomorrow.toISOString().split('T')[0];
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    const depsInput = elements.dependencies.value.trim();
    let dependencies = depsInput ? 
        depsInput.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d)) : 
        [];
    const task = {
        title: elements.taskTitle.value,
        due_date: elements.dueDate.value,
        estimated_hours: elements.estimatedHours.valueAsNumber || parseFloat(elements.estimatedHours.value),
        importance: parseInt(elements.importance.value),
        dependencies: dependencies
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(task)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || errorData.error || 'Failed to create task');
        }
        
        const data = await response.json();
        tasks.push(data.task);
        
        updateTaskList();
        updateAnalyzeButton();
        
        // Store task title for success message before resetting form
        const taskTitle = data.task.title;
       
        elements.taskForm.reset();
        setDefaultDueDate();
        elements.importance.value = 5;
        elements.importanceValue.textContent = '5';
       
        elements.taskTitle.focus();
        
       
        showSuccessMessage(`Task "${taskTitle}" added successfully!`);
        
    } catch (error) {
        showErrorMessage(`Error adding task: ${error.message}`);
    }
}

function updateTaskList() {
    const count = tasks.length;
    elements.taskCount.textContent = count;
    
    if (count === 0) {
        elements.taskList.innerHTML = `
            <div class="empty-state">
                <p>No tasks added yet. Add your first task above!</p>
            </div>
        `;
        return;
    }
    
    elements.taskList.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <div class="task-item-info">
                <div class="task-item-title">${task.id}. ${task.title}</div>
                <div class="task-item-meta">
                    Due: ${formatDate(task.due_date)} • 
                    ${task.estimated_hours}h • 
                    Importance: ${task.importance}/10
                    ${task.dependencies.length > 0 ? ` • Deps: [${task.dependencies.join(', ')}]` : ''}
                </div>
            </div>
            <button class="task-item-remove" onclick="removeTask(${index})">
                Remove
            </button>
        </div>
    `).join('');
}

async function removeTask(index) {
    const task = tasks[index];
    
    const confirmed = await showConfirm(
        `Are you sure you want to delete task "${task.title}"?`,
        'Delete Task',
        'Delete',
        'Cancel',
        'danger'
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        
        const response = await fetch(`${API_BASE_URL}/tasks/${task.id}/`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete task');
        }
        tasks.splice(index, 1);
        updateTaskList();
        updateAnalyzeButton();
        
        showSuccessMessage('Task deleted successfully!');
        
    } catch (error) {
        showErrorMessage(`Error deleting task: ${error.message}`);
    }
}

async function clearAllTasks() {
    if (tasks.length === 0) return;
    
    const confirmed = await showConfirm(
        'Are you sure you want to clear all tasks? This will delete them from the database.',
        'Clear All Tasks',
        'Clear All',
        'Cancel',
        'danger'
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
       
        const response = await fetch(`${API_BASE_URL}/tasks/clear/`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to clear tasks');
        }
        tasks = [];
        updateTaskList();
        updateAnalyzeButton();
        hideResults();
        
        showSuccessMessage('All tasks cleared successfully!');
        
    } catch (error) {
        showErrorMessage(`Error clearing tasks: ${error.message}`);
    }
}

function updateAnalyzeButton() {
    elements.analyzeBtn.disabled = tasks.length === 0;
}

async function handleLoadJson() {
    const jsonText = elements.jsonInput.value.trim();
    
    if (!jsonText) {
        showWarningMessage('Please paste JSON data first.');
        return;
    }
    
    try {
        const data = JSON.parse(jsonText);
        
        if (!data.tasks || !Array.isArray(data.tasks)) {
            throw new Error('JSON must contain a "tasks" array');
        }
      
        const validatedTasks = validateTasksArray(data.tasks);
        
        const response = await fetch(`${API_BASE_URL}/tasks/bulk/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tasks: validatedTasks })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to load tasks');
        }
        
        const result = await response.json();
        
        await loadTasksFromDatabase();
        
        switchTab('form');
        
        let message = `Successfully loaded ${result.created} task(s)!`;
        if (result.errors && result.errors.length > 0) {
            const errorDetails = result.errors.map(err => `${err.task}: ${err.error}`).join(', ');
            showWarningMessage(`${message} However, ${result.errors.length} task(s) failed to load: ${errorDetails}`);
        } else {
            showSuccessMessage(message);
        }
        
    } catch (error) {
        showErrorMessage(`Error loading JSON: ${error.message}`);
    }
}

async function loadExampleData() {
    const exampleData = {
        tasks: [
            {
                title: "Fix critical login bug",
                due_date: "2025-11-28",
                estimated_hours: 2,
                importance: 9,
                dependencies: []
            },
            {
                title: "Update user documentation",
                due_date: "2025-12-15",
                estimated_hours: 8,
                importance: 6,
                dependencies: []
            },
            {
                title: "Write unit tests",
                due_date: "2025-11-30",
                estimated_hours: 5,
                importance: 7,
                dependencies: []
            },
            {
                title: "Code review for feature X",
                due_date: "2025-11-28",
                estimated_hours: 1.5,
                importance: 8,
                dependencies: []
            },
            {
                title: "Deploy to staging",
                due_date: "2025-12-05",
                estimated_hours: 2,
                importance: 8,
                dependencies: []
            }
        ]
    };
    
    try {
     
        const response = await fetch(`${API_BASE_URL}/tasks/bulk/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(exampleData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to load example data');
        }
        
     
        await loadTasksFromDatabase();
        switchTab('form');
        
        showSuccessMessage('Example tasks loaded successfully!');
        
    } catch (error) {
        showErrorMessage(`Error loading example data: ${error.message}`);
    }
}

function validateTasksArray(tasksArray) {
    return tasksArray.map(task => {
        if (!task.title || !task.due_date || 
            task.estimated_hours === undefined || task.importance === undefined) {
            throw new Error('Each task must have: title, due_date, estimated_hours, importance');
        }
        
        const validatedTask = {
            title: String(task.title),
            due_date: String(task.due_date),
            estimated_hours: parseFloat(task.estimated_hours),
            importance: parseInt(task.importance),
            dependencies: Array.isArray(task.dependencies) ? task.dependencies : []
        };
        
       
        if (task.id !== undefined) {
            validatedTask.id = parseInt(task.id);
        }
        
        return validatedTask;
    });
}

function handleStrategyChange(e) {
    const newStrategy = e.target.value;

    if (!strategyDescriptions[newStrategy]) {
        console.error('Invalid strategy:', newStrategy);
        showError('Invalid sorting strategy selected. Please refresh the page.');
        return;
    }
 
    currentStrategy = newStrategy;
    elements.strategyDescription.textContent = strategyDescriptions[currentStrategy];
    
    
    elements.sortingStrategy.classList.add('strategy-changing');
    setTimeout(() => {
        elements.sortingStrategy.classList.remove('strategy-changing');
    }, 300);
    
 
    if (elements.results.style.display !== 'none') {
       
        showSuccessMessage(`Strategy changed to: ${getStrategyDisplayName(currentStrategy)}`);
        analyzeTasks();
    }
}

function getStrategyDisplayName(strategy) {
    const names = {
        smart: 'Smart Balance',
        fastest: 'Fastest Wins',
        impact: 'High Impact',
        deadline: 'Deadline Driven'
    };
    return names[strategy] || strategy;
}


/**
 * Clean up tasks by removing self-dependencies
 * @param {Array} tasks - Array of task objects
 * @returns {Array} Tasks with self-dependencies removed
 */
function cleanTaskDependencies(tasks) {
   
    const validTaskIds = new Set(tasks.map(task => task.id));
    
    return tasks.map(task => {
        if (task.dependencies && Array.isArray(task.dependencies)) {
            
            const cleanedDeps = task.dependencies.filter(depId => {
                if (depId === task.id) {
                    console.warn(`Removed self-dependency from task ${task.id}: ${task.title}`);
                    return false;
                }
                if (!validTaskIds.has(depId)) {
                    console.warn(`Removed non-existent dependency ${depId} from task ${task.id}: ${task.title}`);
                    return false;
                }
                return true;
            });
            return { ...task, dependencies: cleanedDeps };
        }
        return task;
    });
}

async function analyzeTasks() {
  
    if (tasks.length === 0) {
        showError('No tasks to analyze. Please add some tasks first.');
        return;
    }
    if (!currentStrategy || !strategyDescriptions[currentStrategy]) {
        currentStrategy = 'smart'; 
        elements.sortingStrategy.value = 'smart';
        elements.strategyDescription.textContent = strategyDescriptions[currentStrategy];
    }
    
    showLoading();
    
    try {
       
        await loadTasksFromDatabase();
        
        if (tasks.length === 0) {
            throw new Error('No tasks found in database');
        }
        
   
        const cleanedTasks = cleanTaskDependencies(tasks);
        if (!Array.isArray(cleanedTasks) || cleanedTasks.length === 0) {
            throw new Error('Invalid task data. Please check your tasks and try again.');
        }
        const analyzeResponse = await fetch(`${API_BASE_URL}/tasks/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tasks: cleanedTasks })
        });
        
        if (!analyzeResponse.ok) {
            const errorData = await analyzeResponse.json().catch(() => ({}));
            throw new Error(errorData.message || errorData.error || `Analysis failed: ${analyzeResponse.status} ${analyzeResponse.statusText}`);
        }
        
        const analyzeData = await analyzeResponse.json();
        if (!analyzeData.tasks || !Array.isArray(analyzeData.tasks)) {
            throw new Error('Invalid response from server. Please try again.');
        }
        
        let analyzedTasks = analyzeData.tasks;
        if (currentStrategy !== 'smart') {
            analyzedTasks = applySortingStrategy(analyzedTasks, currentStrategy);
        }
        let suggestions = [];
        try {
            const suggestResponse = await fetch(`${API_BASE_URL}/tasks/suggest/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ tasks: cleanedTasks })
            });
            
            if (suggestResponse.ok) {
                const suggestData = await suggestResponse.json();
                suggestions = suggestData.suggestions || [];
            }
        } catch (suggestError) {
            console.warn('Failed to fetch suggestions:', suggestError);
        }
        displayResults(analyzedTasks, suggestions);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'An unexpected error occurred. Please try again.');
    }
}

function applySortingStrategy(tasks, strategy) {
    if (!Array.isArray(tasks) || tasks.length === 0) {
        return tasks;
    }
    
    const sortedTasks = [...tasks];
    
    try {
        switch (strategy) {
            case 'fastest':
                
                sortedTasks.sort((a, b) => {
                    const hoursA = parseFloat(a.estimated_hours) || 0;
                    const hoursB = parseFloat(b.estimated_hours) || 0;
                    return hoursA - hoursB;
                });
                break;
                
            case 'impact':
               
                sortedTasks.sort((a, b) => {
                    const importanceA = parseInt(a.importance) || 0;
                    const importanceB = parseInt(b.importance) || 0;
                    if (importanceB !== importanceA) {
                        return importanceB - importanceA;
                    }
                   
                    return (b.priority_score || 0) - (a.priority_score || 0);
                });
                break;
                
            case 'deadline':
               
                sortedTasks.sort((a, b) => {
                    const dateA = new Date(a.due_date);
                    const dateB = new Date(b.due_date);
                    
       
                    if (isNaN(dateA.getTime()) && isNaN(dateB.getTime())) return 0;
                    if (isNaN(dateA.getTime())) return 1;
                    if (isNaN(dateB.getTime())) return -1;
                    
                    const diff = dateA - dateB;
                  
                    if (diff === 0) {
                        return (b.priority_score || 0) - (a.priority_score || 0);
                    }
                    return diff;
                });
                break;
                
            case 'smart':
            default:
               
                sortedTasks.sort((a, b) => {
                    return (b.priority_score || 0) - (a.priority_score || 0);
                });
                break;
        }
    } catch (error) {
        console.error('Error applying sorting strategy:', error);
      
        return tasks;
    }
    
    return sortedTasks;
}


function showLoading() {
    elements.loadingState.style.display = 'block';
    elements.errorState.style.display = 'none';
    elements.emptyState.style.display = 'none';
    elements.results.style.display = 'none';
    elements.suggestions.style.display = 'none';
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorState.style.display = 'block';
    elements.loadingState.style.display = 'none';
    elements.emptyState.style.display = 'none';
    elements.results.style.display = 'none';
    elements.suggestions.style.display = 'none';
    // Also show as toast notification
    showErrorMessage(message);
}

function hideResults() {
    elements.loadingState.style.display = 'none';
    elements.errorState.style.display = 'none';
    elements.emptyState.style.display = 'block';
    elements.results.style.display = 'none';
    elements.suggestions.style.display = 'none';
}

function displayResults(analyzedTasks, suggestions) {
  
    elements.loadingState.style.display = 'none';
    elements.errorState.style.display = 'none';
    elements.emptyState.style.display = 'none';
    
   
    elements.results.style.display = 'block';
    
    if (elements.strategyIndicator && elements.activeStrategyName) {
        elements.activeStrategyName.textContent = getStrategyDisplayName(currentStrategy);
        elements.strategyIndicator.style.display = 'block';
    }
  
    const highPriorityCount = analyzedTasks.filter(t => 
        getPriorityLevel(t.priority_score) === 'critical' || 
        getPriorityLevel(t.priority_score) === 'high'
    ).length;
    
    const avgScore = analyzedTasks.reduce((sum, t) => sum + (t.priority_score || 0), 0) / analyzedTasks.length;
    
    elements.totalTasks.textContent = analyzedTasks.length;
    elements.highPriority.textContent = highPriorityCount;
    elements.avgScore.textContent = avgScore.toFixed(1);
    
    elements.taskResults.innerHTML = analyzedTasks.map((task, index) => {
        const priorityLevel = getPriorityLevel(task.priority_score);
        const daysUntilDue = getDaysUntilDue(task.due_date);
        
        return `
            <div class="result-card priority-${priorityLevel}">
                <div class="result-rank">#${index + 1}</div>
                
                <div class="result-title">${task.title}</div>
                
                <div class="priority-badge ${priorityLevel}">
                    ${priorityLevel.toUpperCase()} PRIORITY
                    ${task.priority_score ? ` - ${task.priority_score.toFixed(1)}` : ''}
                </div>
                
                <div class="result-meta">
                    <div class="meta-item">
                        <div class="meta-label">Due Date</div>
                        <div class="meta-value">${formatDate(task.due_date)}</div>
                        <small style="color: ${daysUntilDue < 0 ? 'var(--danger)' : 'var(--text-secondary)'}">
                            ${daysUntilDue < 0 ? `${Math.abs(daysUntilDue)} days overdue` : 
                              daysUntilDue === 0 ? 'Due today!' : 
                              `${daysUntilDue} days left`}
                        </small>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Effort</div>
                        <div class="meta-value">${task.estimated_hours}h</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Importance</div>
                        <div class="meta-value">${task.importance}/10</div>
                    </div>
                </div>
                
                ${task.score_breakdown ? `
                    <div class="score-breakdown">
                        <div class="score-item">
                            <span class="score-label">⏰ Urgency</span>
                            <span class="score-value">${task.score_breakdown.urgency_score.toFixed(1)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">⭐ Importance</span>
                            <span class="score-value">${task.score_breakdown.importance_score.toFixed(1)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">⚡ Effort</span>
                            <span class="score-value">${task.score_breakdown.effort_score.toFixed(1)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">🔗 Dependencies</span>
                            <span class="score-value">${task.score_breakdown.dependency_score.toFixed(1)}</span>
                        </div>
                    </div>
                ` : ''}
                
                ${task.dependencies && task.dependencies.length > 0 ? `
                    <div class="result-explanation">
                        <strong>Dependencies:</strong> This task depends on task(s) [${task.dependencies.join(', ')}]
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');

  
    if (suggestions && suggestions.length > 0) {
        elements.suggestions.style.display = 'block';
        elements.suggestionsList.innerHTML = suggestions.map((suggestion, index) => `
            <div class="suggestion-card">
                <div class="suggestion-number">${index + 1}</div>
                <div class="suggestion-title">${suggestion.task.title}</div>
                <div class="suggestion-score">
                    Priority Score: ${suggestion.task.priority_score.toFixed(1)}
                </div>
                <div class="suggestion-reason">
                    💡 ${suggestion.reason}
                </div>
            </div>
        `).join('');
    }
    
    
    loadDependencyGraph();
    
  
    loadEisenhowerMatrix();
}


async function loadTasksFromDatabase() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/`);
        
        if (!response.ok) {
            throw new Error('Failed to load tasks from database');
        }
        
        const data = await response.json();
        tasks = data.tasks || [];
        
   
        tasks = cleanTaskDependencies(tasks);
        
        updateTaskList();
        updateAnalyzeButton();
        
    } catch (error) {
        console.error('Error loading tasks:', error);
        
        tasks = [];
        updateTaskList();
        updateAnalyzeButton();
    }
}


// Toast Notification System
let toastContainer = null;

function getToastContainer() {
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    return toastContainer;
}

function showToast(message, type = 'success', duration = 4000) {
    const container = getToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.success}</span>
        <span class="toast-content">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        toast.classList.add('toast-exiting');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, duration);
    
    return toast;
}

function showSuccessMessage(message) {
    return showToast(message, 'success');
}

function showErrorMessage(message) {
    return showToast(message, 'error', 5000);
}

function showWarningMessage(message) {
    return showToast(message, 'warning', 4500);
}

function showInfoMessage(message) {
    return showToast(message, 'info');
}

function showConfirm(message, title = 'Confirm Action', confirmText = 'Confirm', cancelText = 'Cancel', type = 'warning') {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'confirm-overlay';
        
        const icons = {
            warning: '⚠️',
            danger: '🗑️',
            info: 'ℹ️',
            question: '❓'
        };
        
        overlay.innerHTML = `
            <div class="confirm-dialog">
                <div class="confirm-dialog-header">
                    <span class="confirm-dialog-icon">${icons[type] || icons.warning}</span>
                    <div class="confirm-dialog-title">${title}</div>
                </div>
                <div class="confirm-dialog-message">${message}</div>
                <div class="confirm-dialog-actions">
                    <button class="confirm-btn confirm-btn-secondary" data-action="cancel">${cancelText}</button>
                    <button class="confirm-btn confirm-btn-${type === 'danger' ? 'danger' : 'primary'}" data-action="confirm">${confirmText}</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        const handleClick = (e) => {
            const action = e.target.getAttribute('data-action');
            if (action === 'confirm') {
                overlay.classList.add('toast-exiting');
                setTimeout(() => {
                    overlay.remove();
                }, 300);
                resolve(true);
            } else if (action === 'cancel' || e.target === overlay) {
                overlay.classList.add('toast-exiting');
                setTimeout(() => {
                    overlay.remove();
                }, 300);
                resolve(false);
            }
        };
        
        overlay.addEventListener('click', handleClick);
        
        // Close on Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                overlay.classList.add('toast-exiting');
                setTimeout(() => {
                    overlay.remove();
                }, 300);
                document.removeEventListener('keydown', handleEscape);
                resolve(false);
            }
        };
        document.addEventListener('keydown', handleEscape);
    });
}

function getPriorityLevel(score) {
    if (score >= 80) return 'critical';
    if (score >= 60) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function getDaysUntilDue(dateString) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const dueDate = new Date(dateString);
    dueDate.setHours(0, 0, 0, 0);
    
    const diffTime = dueDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
}

async function loadDependencyGraph() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/dependency-graph/`, {
            method: 'GET'
        });
        
        if (!response.ok) {
            console.warn('Failed to fetch dependency graph:', response.status);
            return; 
        }
        
        const graphData = await response.json();
        
        const graphContainer = document.getElementById('dependencyGraph');
        if (!graphContainer) return;
        
        if (graphData.nodes && graphData.nodes.length > 0) {
            graphContainer.style.display = 'block';
            // Use setTimeout to ensure container is visible before calculating dimensions
            setTimeout(() => {
                renderDependencyGraph(graphData);
            }, 10);
        } else {
            graphContainer.style.display = 'none';
        }
    } catch (error) {
        console.warn('Failed to load dependency graph:', error);
    }
}

function renderDependencyGraph(graphData) {
    const container = document.getElementById('graphContainer');
    if (!container) return;
    
    // Clear container
    container.innerHTML = '';
    
    // Get container dimensions - ensure we have valid dimensions
    const width = Math.max(container.clientWidth || 800, 800);
    const height = 500;
    const padding = 60;
    
    // Create SVG with proper viewBox for scaling
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.style.background = 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)';
    svg.style.display = 'block';
    svg.style.borderRadius = '8px';
    container.appendChild(svg);
    
    // Create defs FIRST (before edges that reference them)
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    
    // Create gradients for nodes
    const normalGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    normalGradient.setAttribute('id', 'nodeGradient');
    normalGradient.setAttribute('x1', '0%');
    normalGradient.setAttribute('y1', '0%');
    normalGradient.setAttribute('x2', '100%');
    normalGradient.setAttribute('y2', '100%');
    const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop1.setAttribute('offset', '0%');
    stop1.setAttribute('stop-color', '#818cf8');
    const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop2.setAttribute('offset', '100%');
    stop2.setAttribute('stop-color', '#6366f1');
    normalGradient.appendChild(stop1);
    normalGradient.appendChild(stop2);
    defs.appendChild(normalGradient);
    
    const cycleGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    cycleGradient.setAttribute('id', 'cycleGradient');
    cycleGradient.setAttribute('x1', '0%');
    cycleGradient.setAttribute('y1', '0%');
    cycleGradient.setAttribute('x2', '100%');
    cycleGradient.setAttribute('y2', '100%');
    const cycleStop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    cycleStop1.setAttribute('offset', '0%');
    cycleStop1.setAttribute('stop-color', '#f87171');
    const cycleStop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    cycleStop2.setAttribute('offset', '100%');
    cycleStop2.setAttribute('stop-color', '#ef4444');
    cycleGradient.appendChild(cycleStop1);
    cycleGradient.appendChild(cycleStop2);
    defs.appendChild(cycleGradient);
    
    // Create shadow filter
    const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
    filter.setAttribute('id', 'shadow');
    filter.setAttribute('x', '-50%');
    filter.setAttribute('y', '-50%');
    filter.setAttribute('width', '200%');
    filter.setAttribute('height', '200%');
    const feGaussianBlur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
    feGaussianBlur.setAttribute('in', 'SourceAlpha');
    feGaussianBlur.setAttribute('stdDeviation', '3');
    const feOffset = document.createElementNS('http://www.w3.org/2000/svg', 'feOffset');
    feOffset.setAttribute('dx', '2');
    feOffset.setAttribute('dy', '2');
    feOffset.setAttribute('result', 'offsetblur');
    const feComponentTransfer = document.createElementNS('http://www.w3.org/2000/svg', 'feComponentTransfer');
    feComponentTransfer.setAttribute('in', 'offsetblur');
    const feFuncA = document.createElementNS('http://www.w3.org/2000/svg', 'feFuncA');
    feFuncA.setAttribute('type', 'linear');
    feFuncA.setAttribute('slope', '0.3');
    feComponentTransfer.appendChild(feFuncA);
    const feMerge = document.createElementNS('http://www.w3.org/2000/svg', 'feMerge');
    const feMergeNode1 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
    feMergeNode1.setAttribute('in', 'SourceGraphic');
    const feMergeNode2 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
    feMergeNode2.setAttribute('in', feComponentTransfer);
    feMerge.appendChild(feMergeNode1);
    feMerge.appendChild(feMergeNode2);
    filter.appendChild(feGaussianBlur);
    filter.appendChild(feOffset);
    filter.appendChild(feComponentTransfer);
    filter.appendChild(feMerge);
    defs.appendChild(filter);
    
    // Create arrow marker for normal edges
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrowhead');
    marker.setAttribute('markerWidth', '12');
    marker.setAttribute('markerHeight', '12');
    marker.setAttribute('refX', '10');
    marker.setAttribute('refY', '3.5');
    marker.setAttribute('orient', 'auto');
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 12 3.5, 0 7');
    polygon.setAttribute('fill', '#64748b');
    marker.appendChild(polygon);
    defs.appendChild(marker);
    
    // Create arrow marker for cycle edges (red)
    const cycleMarker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    cycleMarker.setAttribute('id', 'arrowhead-cycle');
    cycleMarker.setAttribute('markerWidth', '12');
    cycleMarker.setAttribute('markerHeight', '12');
    cycleMarker.setAttribute('refX', '10');
    cycleMarker.setAttribute('refY', '3.5');
    cycleMarker.setAttribute('orient', 'auto');
    const cyclePolygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    cyclePolygon.setAttribute('points', '0 0, 12 3.5, 0 7');
    cyclePolygon.setAttribute('fill', '#ef4444');
    cycleMarker.appendChild(cyclePolygon);
    defs.appendChild(cycleMarker);
    
    svg.appendChild(defs);
    
    const nodes = graphData.nodes;
    const edges = graphData.edges;

    const nodePositions = {};
    const nodeRadius = 28;
    const labelOffset = 45;
    
    // Calculate node positions in a circle with better spacing
    if (nodes.length > 0) {
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width - padding * 2, height - padding * 2) / 2.5;
        
        nodes.forEach((node, i) => {
            const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2; // Start from top
            nodePositions[node.id] = {
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius
            };
        });
    }
    
    // Draw edges with curves (after defs are defined)
    edges.forEach(edge => {
        const from = nodePositions[edge.from];
        const to = nodePositions[edge.to];
        if (from && to) {
            // Calculate control points for curved edge
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const curvature = 0.3;
            
            // Perpendicular vector for curve
            const perpX = -dy / distance;
            const perpY = dx / distance;
            const midX = (from.x + to.x) / 2;
            const midY = (from.y + to.y) / 2;
            const controlX = midX + perpX * distance * curvature;
            const controlY = midY + perpY * distance * curvature;
            
            // Calculate arrow position (offset from node edge)
            const angle = Math.atan2(to.y - from.y, to.x - from.x);
            const arrowX = to.x - Math.cos(angle) * nodeRadius;
            const arrowY = to.y - Math.sin(angle) * nodeRadius;
            const startX = from.x + Math.cos(angle) * nodeRadius;
            const startY = from.y + Math.sin(angle) * nodeRadius;
            
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', `M ${startX} ${startY} Q ${controlX} ${controlY} ${arrowX} ${arrowY}`);
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', edge.inCycle ? '#ef4444' : '#64748b');
            path.setAttribute('stroke-width', edge.inCycle ? '3' : '2');
            path.setAttribute('opacity', '0.7');
            path.setAttribute('marker-end', edge.inCycle ? 'url(#arrowhead-cycle)' : 'url(#arrowhead)');
            path.style.transition = 'all 0.3s ease';
            svg.appendChild(path);
        }
    });
    
    // Draw nodes (on top of edges)
    nodes.forEach(node => {
        const pos = nodePositions[node.id];
        if (pos) {
            // Create group for node
            const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            nodeGroup.setAttribute('class', 'node-group');
            nodeGroup.style.cursor = 'pointer';
            nodeGroup.style.transition = 'transform 0.2s ease';
            
            // Draw circle with gradient and shadow
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', pos.x);
            circle.setAttribute('cy', pos.y);
            circle.setAttribute('r', nodeRadius);
            circle.setAttribute('fill', node.inCycle ? 'url(#cycleGradient)' : 'url(#nodeGradient)');
            circle.setAttribute('stroke', node.inCycle ? '#dc2626' : '#4f46e5');
            circle.setAttribute('stroke-width', '3');
            circle.setAttribute('filter', 'url(#shadow)');
            circle.style.transition = 'all 0.3s ease';
            nodeGroup.appendChild(circle);
            
            // Draw text label (centered properly)
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', pos.x);
            text.setAttribute('y', pos.y);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'middle');
            text.setAttribute('font-size', '14');
            text.setAttribute('font-weight', 'bold');
            text.setAttribute('fill', 'white');
            text.setAttribute('pointer-events', 'none');
            text.textContent = node.id;
            nodeGroup.appendChild(text);
            
            // Draw title label below node
            const titleText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            titleText.setAttribute('x', pos.x);
            titleText.setAttribute('y', pos.y + labelOffset);
            titleText.setAttribute('text-anchor', 'middle');
            titleText.setAttribute('font-size', '11');
            titleText.setAttribute('fill', '#475569');
            titleText.setAttribute('font-weight', '500');
            titleText.setAttribute('pointer-events', 'none');
            const title = node.title || `Task ${node.id}`;
            titleText.textContent = title.length > 20 ? title.substring(0, 20) + '...' : title;
            nodeGroup.appendChild(titleText);
            
            // Add hover effects
            nodeGroup.addEventListener('mouseenter', () => {
                circle.setAttribute('r', nodeRadius + 3);
                circle.setAttribute('stroke-width', '4');
                nodeGroup.style.transform = 'scale(1.1)';
            });
            
            nodeGroup.addEventListener('mouseleave', () => {
                circle.setAttribute('r', nodeRadius);
                circle.setAttribute('stroke-width', '3');
                nodeGroup.style.transform = 'scale(1)';
            });
            
            // Add tooltip on click
            nodeGroup.addEventListener('click', () => {
                const tooltip = document.createElement('div');
                tooltip.style.position = 'absolute';
                tooltip.style.background = 'rgba(0, 0, 0, 0.9)';
                tooltip.style.color = 'white';
                tooltip.style.padding = '8px 12px';
                tooltip.style.borderRadius = '6px';
                tooltip.style.fontSize = '12px';
                tooltip.style.zIndex = '1000';
                tooltip.style.pointerEvents = 'none';
                tooltip.textContent = `Task ${node.id}: ${node.title || 'Untitled'}`;
                document.body.appendChild(tooltip);
                
                const rect = container.getBoundingClientRect();
                tooltip.style.left = (rect.left + pos.x) + 'px';
                tooltip.style.top = (rect.top + pos.y - 50) + 'px';
                
                setTimeout(() => {
                    tooltip.remove();
                }, 2000);
            });
            
            svg.appendChild(nodeGroup);
        }
    });
    
    // Show cycle warning if applicable
    if (graphData.hasCycle) {
        const cycleWarning = document.getElementById('cycleWarning');
        const cyclePath = document.getElementById('cyclePath');
        if (cycleWarning && cyclePath) {
            cycleWarning.style.display = 'block';
            cyclePath.textContent = `Cycle: ${graphData.cyclePath.join(' → ')}`;
        }
    } else {
        const cycleWarning = document.getElementById('cycleWarning');
        if (cycleWarning) {
            cycleWarning.style.display = 'none';
        }
    }
}


async function loadEisenhowerMatrix() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/eisenhower-matrix/`, {
            method: 'GET'
        });
        
        if (!response.ok) {
            return;
        }
        
        const data = await response.json();
        const matrix = data.matrix;
        
        if (matrix) {
            const matrixContainer = document.getElementById('eisenhowerMatrix');
            if (matrixContainer) {
                matrixContainer.style.display = 'block';
                renderEisenhowerMatrix(matrix);
            }
        }
    } catch (error) {
        console.warn('Failed to load Eisenhower Matrix:', error);
    }
}

function renderEisenhowerMatrix(matrix) {
    const quadrants = ['Q1', 'Q2', 'Q3', 'Q4'];
    
    quadrants.forEach(quadrant => {
        const container = document.getElementById(`${quadrant.toLowerCase()}Tasks`);
        if (!container) return;
        
        const tasks = matrix[quadrant] || [];
        
        if (tasks.length === 0) {
            container.innerHTML = '<div class="empty-quadrant">No tasks</div>';
        } else {
            container.innerHTML = tasks.map(task => `
                <div class="matrix-task">
                    <div class="matrix-task-title">${task.title}</div>
                    <div class="matrix-task-meta">
                        <span>Urgency: ${task.urgency_score.toFixed(1)}</span>
                        <span>Importance: ${task.importance_score.toFixed(1)}</span>
                    </div>
                </div>
            `).join('');
        }
    });
}


window.removeTask = removeTask;


