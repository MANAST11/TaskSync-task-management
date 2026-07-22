// API Base URL Configuration
const API_BASE = 'http://localhost:5000/api';

// Toast Notification Helper
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const messageSpan = document.createElement('span');
    messageSpan.className = 'toast-message';
    messageSpan.textContent = message;
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = () => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    };
    
    toast.appendChild(messageSpan);
    toast.appendChild(closeBtn);
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// Authentication Check: Redirect if already logged in
async function checkCurrentSession() {
    try {
        const response = await fetch(`${API_BASE}/current-user`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include' // Crucial to send and receive Flask Session cookies
        });
        
        if (response.ok) {
            const data = await response.json();
            redirectUser(data.user.role);
        }
    } catch (error) {
        console.log("No active session or server offline:", error);
    }
}

// Redirect Helper
function redirectUser(role) {
    if (role === 'administrator') {
        window.location.href = 'admin_dashboard.html';
    } else if (role === 'employee') {
        window.location.href = 'employee_dashboard.html';
    }
}

// Form Submission Event Listener
document.addEventListener('DOMContentLoaded', () => {
    // Check session on load
    checkCurrentSession();

    const form = document.getElementById('login-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        // Toggle Loading State
        submitBtn.disabled = true;
        btnText.textContent = 'Authenticating...';
        btnLoader.style.display = 'block';

        try {
            const response = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
                credentials: 'include' // Important for receiving session cookie
            });

            const data = await response.json();

            if (response.ok) {
                showToast("Login successful! Redirecting...", "success");
                setTimeout(() => {
                    redirectUser(data.user.role);
                }, 1000);
            } else {
                showToast(data.error || "Login failed. Please check your credentials.", "error");
                submitBtn.disabled = false;
                btnText.textContent = 'Sign In';
                btnLoader.style.display = 'none';
            }
        } catch (error) {
            console.error('Error during login:', error);
            showToast("Cannot connect to server. Please verify the backend is running.", "error");
            submitBtn.disabled = false;
            btnText.textContent = 'Sign In';
            btnLoader.style.display = 'none';
        }
    });
});
