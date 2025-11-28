
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
        
       
        elements.taskForm.reset();
        setDefaultDueDate();
        elements.importance.value = 5;
        elements.importanceValue.textContent = '5';
       
        elements.taskTitle.focus();
        
       
        showSuccessMessage('Task added successfully!');
        
    } catch (error) {
        alert(`Error adding task: ${error.message}`);
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
    
    if (!confirm(`Delete task "${task.title}"?`)) {
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
        alert(`Error deleting task: ${error.message}`);
    }
}

async function clearAllTasks() {
    if (tasks.length === 0) return;
    
    if (!confirm('Are you sure you want to clear all tasks? This will delete them from the database.')) {
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
        alert(`Error clearing tasks: ${error.message}`);
    }
}

function updateAnalyzeButton() {
    elements.analyzeBtn.disabled = tasks.length === 0;
}

async function handleLoadJson() {
    const jsonText = elements.jsonInput.value.trim();
    
    if (!jsonText) {
        alert('Please paste JSON data first.');
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
            message += `\n\nFailed to load ${result.errors.length} task(s):`;
            result.errors.forEach(err => {
                message += `\n- ${err.task}: ${err.error}`;
            });
        }
        alert(message);
        
    } catch (error) {
        alert(`Error loading JSON: ${error.message}`);
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
        alert(`Error loading example data: ${error.message}`);
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
                <div class="suggestion-feedback">
                    <button class="btn-feedback btn-helpful" onclick="submitFeedback(${suggestion.task.id}, true)">
                        ✓ Helpful
                    </button>
                    <button class="btn-feedback btn-not-helpful" onclick="submitFeedback(${suggestion.task.id}, false)">
                        ✗ Not Helpful
                    </button>
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


function showSuccessMessage(message) {
   
    const toast = document.createElement('div');
    toast.className = 'success-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
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
            return; 
        }
        
        const graphData = await response.json();
        
        if (graphData.nodes && graphData.nodes.length > 0) {
            const graphContainer = document.getElementById('dependencyGraph');
            if (graphContainer) {
                graphContainer.style.display = 'block';
                renderDependencyGraph(graphData);
            }
        }
    } catch (error) {
        console.warn('Failed to load dependency graph:', error);
    }
}

function renderDependencyGraph(graphData) {
    const container = document.getElementById('graphContainer');
    if (!container) return;
    
   
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '400');
    svg.style.background = 'white';
    container.innerHTML = '';
    container.appendChild(svg);
    
    const nodes = graphData.nodes;
    const edges = graphData.edges;

    const nodePositions = {};
    const nodeRadius = 20;
    const width = container.clientWidth || 800;
    const height = 400;
    
    nodes.forEach((node, i) => {
        const angle = (2 * Math.PI * i) / nodes.length;
        nodePositions[node.id] = {
            x: width / 2 + Math.cos(angle) * Math.min(width, height) / 3,
            y: height / 2 + Math.sin(angle) * Math.min(width, height) / 3
        };
    });
    
    
    edges.forEach(edge => {
        const from = nodePositions[edge.from];
        const to = nodePositions[edge.to];
        if (from && to) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', from.x);
            line.setAttribute('y1', from.y);
            line.setAttribute('x2', to.x);
            line.setAttribute('y2', to.y);
            line.setAttribute('stroke', edge.inCycle ? '#ef4444' : '#64748b');
            line.setAttribute('stroke-width', edge.inCycle ? '3' : '2');
            line.setAttribute('marker-end', 'url(#arrowhead)');
            svg.appendChild(line);
        }
    });
    
 
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrowhead');
    marker.setAttribute('markerWidth', '10');
    marker.setAttribute('markerHeight', '10');
    marker.setAttribute('refX', '9');
    marker.setAttribute('refY', '3');
    marker.setAttribute('orient', 'auto');
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 10 3, 0 6');
    polygon.setAttribute('fill', '#64748b');
    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.appendChild(defs);
    
    nodes.forEach(node => {
        const pos = nodePositions[node.id];
        if (pos) {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', pos.x);
            circle.setAttribute('cy', pos.y);
            circle.setAttribute('r', nodeRadius);
            circle.setAttribute('fill', node.inCycle ? '#ef4444' : '#6366f1');
            circle.setAttribute('stroke', node.inCycle ? '#991b1b' : '#4f46e5');
            circle.setAttribute('stroke-width', '2');
            svg.appendChild(circle);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', pos.x);
            text.setAttribute('y', pos.y + 5);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '12');
            text.setAttribute('fill', 'white');
            text.textContent = node.id;
            svg.appendChild(text);
        }
    });
    
    
    if (graphData.hasCycle) {
        const cycleWarning = document.getElementById('cycleWarning');
        const cyclePath = document.getElementById('cyclePath');
        if (cycleWarning && cyclePath) {
            cycleWarning.style.display = 'block';
            cyclePath.textContent = `Cycle: ${graphData.cyclePath.join(' → ')}`;
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


async function submitFeedback(taskId, wasHelpful) {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/feedback/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_id: taskId,
                was_helpful: wasHelpful,
                feedback_notes: ''
            })
        });
        
        if (response.ok) {
            showSuccessMessage(wasHelpful ? 'Thank you for your feedback!' : 'Feedback recorded. We\'ll improve!');
        } else {
            throw new Error('Failed to submit feedback');
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
        alert('Failed to submit feedback. Please try again.');
    }
}

window.removeTask = removeTask;
window.submitFeedback = submitFeedback;


