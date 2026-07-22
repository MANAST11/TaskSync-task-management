// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Current State
let currentUser = null;
let employeeProfile = null;
let assignmentsData = [];

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
    const loader = document.getElementById('loader-overlay');
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

        if (currentUser.role !== 'employee') {
            window.location.href = 'admin_dashboard.html';
            return;
        }

        employeeProfile = currentUser.employee_details;
        
        // Populate profile sidebar details
        renderProfileInfo();

        // Load dashboard task lists and stats
        await loadDashboardContent();

    } catch (error) {
        console.error("Auth error:", error);
        window.location.href = 'login.html';
    } finally {
        toggleLoader(false);
    }
}

// Render profile panel
function renderProfileInfo() {
    if (!employeeProfile) return;
    
    const fullName = `${employeeProfile.first_name} ${employeeProfile.last_name}`;
    document.getElementById('profile-full-name').textContent = fullName;
    document.getElementById('profile-username').textContent = currentUser.username;
    document.getElementById('profile-email').textContent = employeeProfile.email;
    document.getElementById('profile-phone').textContent = employeeProfile.phone || 'Not provided';
    document.getElementById('profile-dept').textContent = employeeProfile.department_name || 'Unassigned';
    document.getElementById('profile-designation').textContent = employeeProfile.designation || 'None';

    // Initials Avatar
    const initials = (employeeProfile.first_name[0] || '') + (employeeProfile.last_name[0] || '');
    document.getElementById('profile-initials').textContent = initials.toUpperCase() || '?';
    
    // Welcome header greeting
    document.getElementById('welcome-title').textContent = `Welcome, ${employeeProfile.first_name}`;
}

// Load Task and Statistics Data
async function loadDashboardContent() {
    if (!employeeProfile) return;
    toggleLoader(true);
    try {
        // 1. Fetch Stats
        const statsResponse = await fetch(`${API_BASE}/dashboard/stats`, {
            method: 'GET',
            credentials: 'include'
        });
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            document.getElementById('stat-total').textContent = stats.total_assigned;
            document.getElementById('stat-in-progress').textContent = stats.in_progress;
            document.getElementById('stat-completed').textContent = stats.completed;
            document.getElementById('stat-efficiency').textContent = `${stats.completion_percentage}%`;
        }

        // 2. Fetch Tasks Assignments
        const tasksResponse = await fetch(`${API_BASE}/employee/${employeeProfile.id}/tasks`, {
            method: 'GET',
            credentials: 'include'
        });
        if (tasksResponse.ok) {
            assignmentsData = await tasksResponse.json();
            renderTaskCards();
        }

    } catch (e) {
        console.error(e);
        showToast("Error retrieving assignments from server.", "error");
    } finally {
        toggleLoader(false);
    }
}

// Render Task Board cards
function renderTaskCards() {
    const grid = document.getElementById('task-grid-container');
    grid.innerHTML = '';

    if (assignmentsData.length === 0) {
        grid.innerHTML = `
            <div style="text-align: center; color: var(--text-muted); grid-column: 1/-1; padding: 40px;">
                🎉 No tasks currently assigned to you!
            </div>
        `;
        return;
    }

    assignmentsData.forEach(a => {
        const card = document.createElement('div');
        card.className = 'task-card glass-panel';
        
        const remarksHtml = a.remarks ? 
            `<div class="task-card-remarks">"${escapeHTML(a.remarks)}"</div>` : '';
            
        card.innerHTML = `
            <div class="task-card-header">
                <span class="task-title">${escapeHTML(a.task_title)}</span>
                <span class="badge badge-${a.task_priority}">${a.task_priority}</span>
            </div>
            
            <p class="task-desc">${escapeHTML(a.task_description || 'No description provided.')}</p>

            <div class="progress-bar-container">
                <div class="progress-bar-label">
                    <span style="color: var(--text-secondary);">Progress</span>
                    <span style="color: #FFF;">${a.completion_percentage}%</span>
                </div>
                <div class="progress-bar-track">
                    <div class="progress-bar-fill" style="width: ${a.completion_percentage}%"></div>
                </div>
            </div>

            ${remarksHtml}

            <div class="task-card-meta">
                <span>⏱️ Est: ${a.task_estimated_hours} hrs</span>
                <span class="badge badge-${a.status}">${a.status.replace('_', ' ')}</span>
            </div>

            <button class="btn btn-primary" onclick="openUpdateStatusModal(${a.id})" style="width: 100%; margin-top: 10px;">
                🔄 Update Progress
            </button>
        `;
        grid.appendChild(card);
    });
}

// Open Progress Dialog Modal
function openUpdateStatusModal(assignmentId) {
    const assignment = assignmentsData.find(a => a.id === assignmentId);
    if (!assignment) return;

    document.getElementById('modal-assignment-id').value = assignment.id;
    document.getElementById('modal-task-title').value = assignment.task_title;
    document.getElementById('modal-status-select').value = assignment.status;
    document.getElementById('modal-pct-slider').value = assignment.completion_percentage;
    document.getElementById('pct-display').textContent = assignment.completion_percentage;
    document.getElementById('modal-remarks').value = assignment.remarks || '';

    openModal('status-modal');
}

// Modal display controls
function openModal(id) {
    document.getElementById(id).classList.add('active');
}
function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// Submit progress updates
async function submitProgressUpdate(e) {
    e.preventDefault();
    const id = document.getElementById('modal-assignment-id').value;
    const status = document.getElementById('modal-status-select').value;
    const completion_percentage = parseInt(document.getElementById('modal-pct-slider').value);
    const remarks = document.getElementById('modal-remarks').value.trim();

    try {
        toggleLoader(true);
        const response = await fetch(`${API_BASE}/assignment/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status, completion_percentage, remarks }),
            credentials: 'include'
        });

        const data = await response.json();
        if (response.ok) {
            showToast(data.message, 'success');
            closeModal('status-modal');
            await loadDashboardContent();
        } else {
            showToast(data.error || "Failed to update task", 'error');
        }
    } catch (err) {
        console.error(err);
        showToast("Server connection error.", "error");
    } finally {
        toggleLoader(false);
    }
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
    // Authenticate
    authenticateUser();

    // Link Slider value indicator changes
    const slider = document.getElementById('modal-pct-slider');
    const display = document.getElementById('pct-display');
    const statusSelect = document.getElementById('modal-status-select');

    slider.addEventListener('input', () => {
        display.textContent = slider.value;
    });

    // Auto update progress rules based on status dropdown
    statusSelect.addEventListener('change', () => {
        if (statusSelect.value === 'completed') {
            slider.value = 100;
            display.textContent = 100;
        } else if (statusSelect.value === 'pending') {
            slider.value = 0;
            display.textContent = 0;
        } else if (statusSelect.value === 'in_progress' && parseInt(slider.value) === 100) {
            slider.value = 90;
            display.textContent = 90;
        }
    });

    // Form Event submit handlers
    document.getElementById('status-form').addEventListener('submit', submitProgressUpdate);

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
});
