# TaskSync: Enterprise Task Management System

An enterprise-grade, clean architecture Task Management System designed for organization-wide task delegation, progression tracking, and audit logging. 

Features role-based access for two user groups:
1. **Administrators**: Manage departments, employees, create, assign, and track tasks, and view full system activity logs.
2. **Employees**: View assigned tasks, update progression percentages, status states (Pending, In Progress, Completed), write logs/comments, and edit workspace profiles.

---

## Technical Stack & Architecture

- **Backend**: Python, Flask, SQLAlchemy ORM, Flask Blueprints, Flask-Session (secure server-side filesystem sessions), Flask-CORS.
- **Frontend**: HTML5, CSS3 (Premium dark-mode glassmorphic interface, Inter font, custom variables), Vanilla JavaScript (Fetch API with credentials enabled).
- **Database**: MySQL (Production support) / SQLite (Development zero-dependency fallback).
- **Design Architecture**:
  - **Application Factory Pattern**: Decoupled environment configuration and dynamic app context startup.
  - **Layered Service Pattern**: Route handlers only handle request/response parameters, delegating all domain logic and validations to standalone services (`employee_service.py`, `task_service.py`, etc.).
  - **Audit Logging**: Interceptors write database logs for all mutations (creating tasks, assignments, logins, logouts, etc.).

---

## Directory Structure

```text
task-management/
├── backend/
│   ├── run.py                 # Backend server entry point
│   ├── requirements.txt       # Dependency definitions
│   ├── seed.py                # Database creation & mock data seeder
│   └── task_management/
│       ├── __init__.py        # App factory & blueprint bindings
│       ├── config.py          # Port/Database settings (supports MySQL & SQLite)
│       ├── extensions.py      # Shared SQLAlchemy & Session instances
│       ├── models/            # SQLAlchemy database ORM models
│       ├── routes/            # Blueprint API request controllers
│       ├── services/          # Decoupled business logic services
│       └── utils/             # Authorization decorators
├── frontend/
│   ├── login.html             # Auth landing page
│   ├── admin_dashboard.html   # Administrator SPA board
│   ├── employee_dashboard.html# Employee workspace SPA board
│   ├── css/
│   │   └── styles.css         # Custom responsive layout & design system
│   └── js/
│       ├── login.js           # Authentication handler
│       ├── admin_dashboard.js # Admin views, CRUD, and pagination controller
│       └── employee_dashboard.js# Employee progress, slider, and profile controller
├── database/
│   ├── schema.sql             # SQL Schema definition (MySQL)
│   └── sample_data.sql        # Reference SQL sample queries
└── README.md                  # System Documentation
```

---

## Installation & Setup Guide

### 1. Prerequisite Setup (Local SQLite Development)
To run the system with zero database dependencies (falls back to a local `task_manager.db` file in the backend folder):

1. **Clone the repository** and navigate to the project directory.
2. **Create and Activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. **Seed the database** (Creates schema and populates sample records):
   ```bash
   python backend/seed.py
   ```
5. **Run the server**:
   ```bash
   python backend/run.py
   ```
   The backend API will run on `http://localhost:5000`.

---

### 2. Database Integration (Production MySQL Setup)
To switch to a MySQL server:
1. Create a database in MySQL:
   ```sql
   CREATE DATABASE task_management_db;
   ```
2. Define the following Environment Variables before running the backend:
   ```bash
   # Windows PowerShell
   $env:DB_USER="your_mysql_user"
   $env:DB_PASSWORD="your_mysql_password"
   $env:DB_HOST="localhost"
   $env:DB_PORT="3306"
   $env:DB_NAME="task_management_db"
   ```
   *Note: If these env variables are loaded, SQLAlchemy automatically hooks to the MySQL connection instead of SQLite.*

---

## How to Run Frontend
Because the frontend is static HTML/JS communicating with the backend API via AJAX CORS requests, you can serve it via any basic local server.

### Option A: VS Code Live Server (Recommended)
1. Open the project folder in VS Code.
2. Right-click `frontend/login.html` and select **"Open with Live Server"**.
3. It will host the frontend on `http://127.0.0.1:5500/frontend/login.html` (which is already configured in backend CORS permissions).

### Option B: Python SimpleHTTPServer
In a separate terminal, serve from the workspace root:
```bash
python -m http.server 8000
```
Navigate to `http://localhost:8000/frontend/login.html`.

---

## Mock User Credentials (Seeded Defaults)

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| **admin** | `password123` | Administrator | Fully-privileged organization administrator |
| **jdoe** | `password123` | Employee | John Doe (Senior Backend Engineer) |
| **asmith** | `password123` | Employee | Alice Smith (QA Automation Engineer) |
| **mwilliams** | `password123` | Employee | Mark Williams (Product Owner) |

---

## API Documentation

### Authentication Blueprints
- `POST /api/login` - JSON request `{ "username": "admin", "password": "password123" }` to verify credentials and set up session.
- `POST /api/logout` - Clear user session.
- `GET /api/current-user` - Retrieve session user details and profile.

### Employee Blueprints (Admin only)
- `GET /api/employees` - List all employees and status properties.
- `POST /api/employees` - Register employee account and details.
- `PUT /api/employees/<id>` - Modify employee details, status, or credentials.
- `DELETE /api/employees/<id>` - Delete employee and cascade-delete auth user.

### Department Blueprints
- `GET /api/departments` - List all departments.
- `POST /api/departments` - Add a new department (Admin only).

### Task Blueprints
- `GET /api/tasks` - List tasks. Supports sorting headers, query search, priority/status filtering, and page pagination.
- `GET /api/tasks/<id>` - Retrieve details for a single task.
- `POST /api/tasks` - Create a new task (Admin only).
- `PUT /api/tasks/<id>` - Update task descriptions, priorities, etc. (Admin only).
- `DELETE /api/tasks/<id>` - Soft delete a task (Admin only).

### Assignment Blueprints
- `POST /api/assign` - Assign a task to an employee (Admin only).
- `PUT /api/assignment/<id>` - Update progress percentage, remarks, and state.
- `GET /api/employee/<id>/tasks` - Fetch active and completed tasks for an employee.

### Dashboard Stats
- `GET /api/dashboard/stats` - Fetch overall statistics (aggregate stats for admins, individual charts for employees).
- `GET /api/activity-logs` - Fetch audit trails (Admin only).
