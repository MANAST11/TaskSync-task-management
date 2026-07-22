// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Current State
let currentUser = null;
let currentTab = 'overview-section';
let tasksData = [];
let employeesList = [];
let departmentsList = [];

// Tasks pagination and filtering state
let taskFilters = {
    search: '',
    priority: '',
    status: '',
    sort_by: 'created_at',
    sort_dir: 'desc',
    page: 1,
    limit: 10
};

// Toast notification helper
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// Loading overlay control
function toggleLoader(show) {
    const loader = document.getElementById('workspace-loader');
    if (loader) {
        if (show) loader.classList.add('active');
        else loader.classList.remove('active');
    }
}

// Check session on load
async function authenticateUser() {
    toggleLoader(true);
    try {
        const response = await fetch(`${API_BASE}/current-user`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) {
            window.location.href = 'login.html';
            return;
        }

        const data = await response.json();
        currentUser = data.user;

        if (currentUser.role !== 'administrator') {
            window.location.href = 'employee_dashboard.html';
            return;
        }

        // Set username display
        document.getElementById('user-display-name').textContent = currentUser.username;
        
        // Initial data load
        await loadAllDashboardData();
    } catch (error) {
        console.error("Auth error:", error);
        window.location.href = 'login.html';
    } finally {
        toggleLoader(false);
    }
}

// Load data based on active tab
async function loadAllDashboardData() {
    toggleLoader(true);
    try {
        await loadDepartments(); // Needed as lookup for employees/tasks
        await loadEmployees();   // Needed for task allocation
        
        if (currentTab === 'overview-section') {
            await loadOverviewStats();
        } else if (currentTab === 'tasks-section') {
            await loadTasks();
        } else if (currentTab === 'employees-section') {
            await loadEmployees(); // reload directory list
        } else if (currentTab === 'departments-section') {
            await loadDepartments(); // reload dept list
        } else if (currentTab === 'activity-section') {
            await loadAllLogs();
        }
    } catch (error) {
        console.error("Error loading dashboard data:", error);
        showToast("Error retrieving organization records.", "error");
    } finally {
        toggleLoader(false);
    }
}

// 1. Load Overview Statistics
async function loadOverviewStats() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/stats`, {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) throw new Error();
        
        const data = await response.json();
        
        // Update summary numbers
        document.getElementById('stat-total-tasks').textContent = data.counts.tasks;
        document.getElementById('stat-pending-tasks').textContent = data.counts.assignments_pending + data.counts.assignments_in_progress;
        document.getElementById('stat-completed-tasks').textContent = data.counts.assignments_completed;
        document.getElementById('stat-employee-count').textContent = data.counts.employees;
        
        // Render Recent Assignments Table
        const recentBody = document.getElementById('recent-assignments-body');
        recentBody.innerHTML = '';
        if (data.recent_assignments.length === 0) {
            recentBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No assignments yet.</td></tr>';
        } else {
            data.recent_assignments.forEach(a => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${escapeHTML(a.task_title)}</strong></td>
                    <td>${escapeHTML(a.employee_name)}</td>
                    <td><span class="badge badge-${a.status}">${a.status.replace('_', ' ')}</span></td>
                    <td>
                        <div style="display:flex; align-items:center; gap: 8px;">
                            <span style="font-size: 0.8rem; font-weight:600;">${a.completion_percentage}%</span>
                        </div>
                    </td>
                `;
                recentBody.appendChild(tr);
            });
        }
        
        // Render Recent Activity Logs
        const logsBody = document.getElementById('recent-logs-body');
        logsBody.innerHTML = '';
        if (data.recent_activities.length === 0) {
            logsBody.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 20px;">No system activities.</div>';
        } else {
            data.recent_activities.forEach(log => {
                const div = document.createElement('div');
                div.className = 'log-item';
                div.innerHTML = `
                    <div class="log-item-header">
                        <span class="log-action">${log.action}</span>
                        <span class="log-time">${new Date(log.created_at).toLocaleString()}</span>
                    </div>
                    <div class="log-desc">${escapeHTML(log.description)} <span style="font-size:0.75rem; color:var(--text-muted);">by ${log.username}</span></div>
                `;
                logsBody.appendChild(div);
            });
        }
    } catch (e) {
        console.error(e);
        showToast("Failed to fetch dashboard overview metrics", "error");
    }
}

// 2. Load and Filter Tasks Table
async function loadTasks() {
    try {
        const queryParams = new URLSearchParams(taskFilters).toString();
        const response = await fetch(`${API_BASE}/tasks?${queryParams}`, {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) throw new Error();
        
        const data = await response.json();
        tasksData = data.tasks;
        
        // Render Tasks
        const body = document.getElementById('tasks-table-body');
        body.innerHTML = '';
        
        if (tasksData.length === 0) {
            body.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No tasks found matching current filters.</td></tr>';
        } else {
            tasksData.forEach(task => {
                const tr = document.createElement('tr');
                
                // Format assignees
                let assigneesHtml = '<span style="color:var(--text-muted); font-size:0.8rem;">Unassigned</span>';
                if (task.assignments && task.assignments.length > 0) {
                    assigneesHtml = task.assignments.map(a => 
                        `<div style="margin-bottom: 2px;">
                            <strong>${escapeHTML(a.employee_name)}</strong> 
                            <span class="badge badge-${a.status}" style="font-size: 0.65rem; padding: 1px 4px;">${a.status.replace('_', ' ')} (${a.completion_percentage}%)</span>
                         </div>`
                    ).join('');
                }
                
                tr.innerHTML = `
                    <td>
                        <div style="font-weight:600; color:#FFF;">${escapeHTML(task.title)}</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary); max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            ${escapeHTML(task.description || 'No description.')}
                        </div>
                    </td>
                    <td><span class="badge badge-${task.priority}">${task.priority}</span></td>
                    <td>${task.estimated_hours} hrs</td>
                    <td>${assigneesHtml}</td>
                    <td>${new Date(task.created_at).toLocaleDateString()}</td>
                    <td style="text-align: right;">
                        <div class="action-btns" style="justify-content: flex-end;">
                            <button class="btn btn-secondary btn-icon btn-icon" onclick="openAssignModal(${task.id}, '${escapeHTML(task.title)}')">Assign</button>
                            <button class="btn btn-secondary btn-icon" style="color: var(--secondary);" onclick="openEditTaskModal(${task.id})">Edit</button>
                            <button class="btn btn-danger btn-icon" onclick="deleteTask(${task.id})">Delete</button>
                        </div>
                    </td>
                `;
                body.appendChild(tr);
            });
        }
        
        // Update pagination UI
        document.getElementById('task-pagination-info').textContent = 
            `Showing page ${data.current_page} of ${data.pages || 1} (Total: ${data.total} tasks)`;
        
        document.getElementById('task-prev-btn').disabled = data.current_page <= 1;
        document.getElementById('task-next-btn').disabled = data.current_page >= data.pages;
        
    } catch (e) {
        console.error(e);
        showToast("Failed to fetch task list", "error");
    }
}

// 3. Load Employee Directory
async function loadEmployees() {
    try {
        const response = await fetch(`${API_BASE}/employees`, {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) throw new Error();
        
        employeesList = await response.json();
        
        const body = document.getElementById('employees-table-body');
        if (body) {
            body.innerHTML = '';
            if (employeesList.length === 0) {
                body.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No employees registered.</td></tr>';
            } else {
                employeesList.forEach(e => {
                    const tr = document.createElement('tr');
                    const statusBadge = `<span class="badge ${e.status === 'active' ? 'badge-completed' : 'badge-pending'}">${e.status}</span>`;
                    
                    tr.innerHTML = `
                        <td><strong>${escapeHTML(e.first_name)} ${escapeHTML(e.last_name)}</strong></td>
                        <td>${escapeHTML(e.username || '')}</td>
                        <td>${escapeHTML(e.email)}</td>
                        <td>${escapeHTML(e.department_name || 'Unassigned')}</td>
                        <td>${escapeHTML(e.designation || 'None')}</td>
                        <td>${statusBadge}</td>
                        <td style="text-align: right;">
                            <div class="action-btns" style="justify-content: flex-end;">
                                <button class="btn btn-secondary btn-icon" onclick="openEditEmployeeModal(${e.id})">Edit</button>
                                <button class="btn btn-danger btn-icon" onclick="deleteEmployee(${e.id})">Delete</button>
                            </div>
                        </td>
                    `;
                    body.appendChild(tr);
                });
            }
        }
        
        // Update Employee Selects in Modal dropdowns
        const assignSelect = document.getElementById('assign-employee-select');
        if (assignSelect) {
            assignSelect.innerHTML = '<option value="" disabled selected>Select an employee...</option>';
            employeesList.forEach(e => {
                if (e.status === 'active') {
                    const opt = document.createElement('option');
                    opt.value = e.id;
                    opt.textContent = `${e.first_name} ${e.last_name} (${e.designation || 'No title'})`;
                    assignSelect.appendChild(opt);
                }
            });
        }
    } catch (e) {
        console.error(e);
    }
}

// 4. Load Departments
async function loadDepartments() {
    try {
        const response = await fetch(`${API_BASE}/departments`, {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) throw new Error();
        
        departmentsList = await response.json();
        
        const body = document.getElementById('departments-table-body');
        if (body) {
            body.innerHTML = '';
            if (departmentsList.length === 0) {
                body.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No departments configured.</td></tr>';
            } else {
                departmentsList.forEach(d => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${escapeHTML(d.name)}</strong></td>
                        <td>${escapeHTML(d.description || 'No description provided.')}</td>
                        <td style="text-align: right; color: var(--text-muted); font-size: 0.8rem;">System Managed</td>
                    `;
                    body.appendChild(tr);
                });
            }
        }
        
        // Update Department Select in Employee Modal
        const deptSelect = document.getElementById('emp-dept-select');
        if (deptSelect) {
            deptSelect.innerHTML = '<option value="">No Department</option>';
            departmentsList.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d.id;
                opt.textContent = d.name;
                deptSelect.appendChild(opt);
            });
        }
    } catch (e) {
        console.error(e);
    }
}

// 5. Load all Logs
async function loadAllLogs() {
    try {
        const response = await fetch(`${API_BASE}/activity-logs`, {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) throw new Error();
        const data = await response.json();
        
        const container = document.getElementById('full-logs-body');
        container.innerHTML = '';
        
        if (data.length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 30px;">No activity history recorded yet.</div>';
        } else {
            data.forEach(log => {
                const div = document.createElement('div');
                div.className = 'log-item';
                div.style.marginBottom = '8px';
                div.innerHTML = `
                    <div class="log-item-header">
                        <span class="log-action">${log.action}</span>
                        <span class="log-time">${new Date(log.created_at).toLocaleString()}</span>
                    </div>
                    <div class="log-desc">
                        ${escapeHTML(log.description)} 
                        <span style="font-size:0.75rem; color:var(--text-muted); float: right;">Logged by: <strong>${log.username}</strong></span>
                    </div>
                `;
                container.appendChild(div);
            });
        }
    } catch (e) {
        console.error(e);
    }
}

// CRUD: Tasks Management
async function saveTask(e) {
    e.preventDefault();
    const id = document.getElementById('task-form-id').value;
    const title = document.getElementById('task-title').value.trim();
    const description = document.getElementById('task-desc').value.trim();
    const priority = document.getElementById('task-priority').value;
    const estimated_hours = document.getElementById('task-hours').value;

    const payload = { title, description, priority, estimated_hours };
    const url = id ? `${API_BASE}/tasks/${id}` : `${API_BASE}/tasks`;
    const method = id ? 'PUT' : 'POST';

    try {
        toggleLoader(true);
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            credentials: 'include'
        });

        const data = await response.json();
        if (response.ok) {
            showToast(data.message, 'success');
            closeModal('task-modal');
            await loadTasks();
        } else {
            showToast(data.error || "Failed to save task", 'error');
        }
    } catch (err) {
        console.error(err);
        showToast("Server communication error.", "error");
    } finally {
        toggleLoader(false);
    }
}

async function deleteTask(id) {
    if (!confirm("Are you sure you want to soft-delete this task? It will be removed from all active boards.")) return;
    
    try {
        toggleLoader(true);
        const response = await fetch(`${API_BASE}/tasks/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, 'success');
            await loadTasks();
        } else {
            showToast(data.error, 'error');
        }
    } catch (err) {
        console.error(err);
    } finally {
        toggleLoader(false);
    }
}

// CRUD: Employee Management
async function saveEmployee(e) {
    e.preventDefault();
    const id = document.getElementById('employee-form-id').value;
    const first_name = document.getElementById('emp-first-name').value.trim();
    const last_name = document.getElementById('emp-last-name').value.trim();
    const email = document.getElementById('emp-email').value.trim();
    const phone = document.getElementById('emp-phone').value.trim();
    const department_id = document.getElementById('emp-dept-select').value;
    const designation = document.getElementById('emp-designation').value.trim();
    
    const payload = { first_name, last_name, email, phone, designation };
    if (department_id) payload.department_id = parseInt(department_id);

    if (!id) {
        // Create requires password and username
        payload.username = document.getElementById('emp-username').value.trim();
        payload.password = document.getElementById('emp-password').value;
    } else {
        // Edit optionally supports password reset and status
        const password = document.getElementById('emp-password').value;
        if (password) payload.password = password;
        payload.status = document.getElementById('emp-status').value;
    }

    const url = id ? `${API_BASE}/employees/${id}` : `${API_BASE}/employees`;
    const method = id ? 'PUT' : 'POST';

    try {
        toggleLoader(true);
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            credentials: 'include'
        });

        const data = await response.json();
        if (response.ok) {
            showToast(data.message, 'success');
            closeModal('employee-modal');
            await loadEmployees();
        } else {
            showToast(data.error || "Failed to save employee profile", 'error');
        }
    } catch (err) {
        console.error(err);
    } finally {
        toggleLoader(false);
    }
}

async function deleteEmployee(id) {
    if (!confirm("Are you sure you want to permanently delete this employee account? This cascades and removes all their details!")) return;
    
    try {
        toggleLoader(true);
        const response = await fetch(`${API_BASE}/employees/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, 'success');
            await loadEmployees();
        } else {
            showToast(data.error, 'error');
        }
    } catch (err) {
        console.error(err);
    } finally {
        toggleLoader(false);
    }
}

// CRUD: Department
async function saveDepartment(e) {
    e.preventDefault();
    const name = document.getElementById('dept-name').value.trim();
    const description = document.getElementById('dept-desc').value.trim();

    try {
        toggleLoader(true);
        const response = await fetch(`${API_BASE}/departments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description }),
            credentials: 'include'
        });

        const data = await response.json();
        if (response.ok) {
            showToast(data.message, 'success');
            closeModal('department-modal');
            await loadDepartments();
        } else {
            showToast(data.error, 'error');
        }
    } catch (err) {
        console.error(err);
    } finally {
        toggleLoader(false);
    }
}

// Assign Task Submission
async function submitAssign(e) {
    e.preventDefault();
    const task_id = parseInt(document.getElementById('assign-task-id').value);
    const employee_id = parseInt(document.getElementById('assign-employee-select').value);

    try {
        toggleLoader(true);
        const response = await fetch(`${API_BASE}/assign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id, employee_id }),
            credentials: 'include'
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, 'success');
            closeModal('assign-modal');
            await loadTasks();
        } else {
            showToast(data.error, 'error');
        }
    } catch (err) {
        console.error(err);
    } finally {
        toggleLoader(false);
    }
}

// Modal Toggle Handlers
function openModal(id) {
    document.getElementById(id).classList.add('active');
}
function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// Modal open details
function openCreateTaskModal() {
    document.getElementById('task-form-id').value = '';
    document.getElementById('task-modal-title').textContent = 'Create New Task';
    document.getElementById('task-form').reset();
    openModal('task-modal');
}

function openEditTaskModal(id) {
    const task = tasksData.find(t => t.id === id);
    if (!task) return;
    
    document.getElementById('task-form-id').value = task.id;
    document.getElementById('task-modal-title').textContent = 'Edit Task Details';
    document.getElementById('task-title').value = task.title;
    document.getElementById('task-desc').value = task.description || '';
    document.getElementById('task-priority').value = task.priority;
    document.getElementById('task-hours').value = task.estimated_hours;
    
    openModal('task-modal');
}

function openAssignModal(id, title) {
    document.getElementById('assign-task-id').value = id;
    document.getElementById('assign-task-title').value = title;
    openModal('assign-modal');
}

function openCreateEmployeeModal() {
    document.getElementById('employee-form-id').value = '';
    document.getElementById('employee-modal-title').textContent = 'Add Employee Account';
    document.getElementById('employee-form').reset();
    
    // Show fields that are required for new account
    document.getElementById('emp-username-container').style.display = 'block';
    document.getElementById('emp-username').required = true;
    document.getElementById('emp-password-label').textContent = 'Password';
    document.getElementById('emp-password').required = true;
    document.getElementById('emp-status-container').style.display = 'none';
    
    openModal('employee-modal');
}

function openEditEmployeeModal(id) {
    const e = employeesList.find(emp => emp.id === id);
    if (!e) return;

    document.getElementById('employee-form-id').value = e.id;
    document.getElementById('employee-modal-title').textContent = 'Edit Employee Profile';
    document.getElementById('emp-first-name').value = e.first_name;
    document.getElementById('emp-last-name').value = e.last_name;
    document.getElementById('emp-email').value = e.email;
    document.getElementById('emp-phone').value = e.phone || '';
    document.getElementById('emp-dept-select').value = e.department_id || '';
    document.getElementById('emp-designation').value = e.designation || '';
    
    // Hide / adjust fields that aren't editable directly
    document.getElementById('emp-username-container').style.display = 'none';
    document.getElementById('emp-username').required = false;
    document.getElementById('emp-password-label').textContent = 'Reset Password (Optional)';
    document.getElementById('emp-password').required = false;
    document.getElementById('emp-password').value = '';
    
    // Show status dropdown
    document.getElementById('emp-status-container').style.display = 'block';
    document.getElementById('emp-status').value = e.status || 'active';
    
    openModal('employee-modal');
}

function openCreateDepartmentModal() {
    document.getElementById('department-form').reset();
    openModal('department-modal');
}

// Utilities
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

// Event Listeners Initializer
document.addEventListener('DOMContentLoaded', () => {
    // Check login
    authenticateUser();

    // Sidebar navigation switching
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', async (e) => {
            document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            const target = link.getAttribute('data-target');
            document.querySelectorAll('.dashboard-section').forEach(sec => sec.classList.remove('active'));
            document.getElementById(target).classList.add('active');
            
            currentTab = target;
            await loadAllDashboardData();
        });
    });

    // Form Event Submit Listeners
    document.getElementById('task-form').addEventListener('submit', saveTask);
    document.getElementById('assign-form').addEventListener('submit', submitAssign);
    document.getElementById('employee-form').addEventListener('submit', saveEmployee);
    document.getElementById('department-form').addEventListener('submit', saveDepartment);

    // Logout
    document.getElementById('logout-btn').addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE}/logout`, { method: 'POST', credentials: 'include' });
            if (response.ok) {
                showToast("Logged out successfully.", "success");
                setTimeout(() => window.location.href = 'login.html', 1000);
            }
        } catch (e) {
            console.error(e);
        }
    });

    // Task Filter Submit Buttons
    document.getElementById('task-filter-btn').addEventListener('click', () => {
        taskFilters.search = document.getElementById('task-search-input').value;
        taskFilters.priority = document.getElementById('task-priority-filter').value;
        taskFilters.status = document.getElementById('task-status-filter').value;
        taskFilters.page = 1;
        loadTasks();
    });

    document.getElementById('task-reset-btn').addEventListener('click', () => {
        document.getElementById('task-search-input').value = '';
        document.getElementById('task-priority-filter').value = '';
        document.getElementById('task-status-filter').value = '';
        
        taskFilters.search = '';
        taskFilters.priority = '';
        taskFilters.status = '';
        taskFilters.page = 1;
        loadTasks();
    });

    // Task table sorting click listeners
    document.querySelectorAll('#tasks-section th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.getAttribute('data-sort');
            if (taskFilters.sort_by === field) {
                taskFilters.sort_dir = taskFilters.sort_dir === 'desc' ? 'asc' : 'desc';
            } else {
                taskFilters.sort_by = field;
                taskFilters.sort_dir = 'desc';
            }
            loadTasks();
        });
    });

    // Task Pagination controls
    document.getElementById('task-prev-btn').addEventListener('click', () => {
        if (taskFilters.page > 1) {
            taskFilters.page--;
            loadTasks();
        }
    });

    document.getElementById('task-next-btn').addEventListener('click', () => {
        taskFilters.page++;
        loadTasks();
    });
});
