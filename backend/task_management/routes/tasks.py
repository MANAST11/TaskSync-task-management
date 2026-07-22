from flask import Blueprint, request, jsonify, session
from task_management.services.task_service import TaskService
from task_management.utils.auth_helpers import login_required, admin_required

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Retrieve filtered, sorted, paginated tasks list."""
    filters = {
        'search': request.args.get('search', ''),
        'priority': request.args.get('priority', ''),
        'status': request.args.get('status', ''),
        'employee_id': request.args.get('employee_id'),
        'sort_by': request.args.get('sort_by', 'created_at'),
        'sort_dir': request.args.get('sort_dir', 'desc'),
        'page': request.args.get('page', 1),
        'limit': request.args.get('limit', 10)
    }
    
    user_id = session.get('user_id')
    role = session.get('role')
    
    # If the user is an employee, get their employee profile ID
    employee_id = None
    if role == 'employee':
        from task_management.models import Employee
        emp = Employee.query.filter_by(user_id=user_id).first()
        if emp:
            employee_id = emp.id

    result, status_code = TaskService.get_tasks(filters, user_id, role, employee_id)
    return jsonify(result), status_code

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Retrieve details for a single task."""
    user_id = session.get('user_id')
    role = session.get('role')
    
    employee_id = None
    if role == 'employee':
        from task_management.models import Employee
        emp = Employee.query.filter_by(user_id=user_id).first()
        if emp:
            employee_id = emp.id

    result, status_code = TaskService.get_task_by_id(task_id, user_id, role, employee_id)
    return jsonify(result), status_code

@tasks_bp.route('/tasks', methods=['POST'])
@admin_required
def create_task():
    """Create a new task (Admin only)."""
    data = request.get_json() or {}
    admin_id = session.get('user_id')
    result, status_code = TaskService.create_task(data, admin_id)
    return jsonify(result), status_code

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@admin_required
def update_task(task_id):
    """Update details of an existing task (Admin only)."""
    data = request.get_json() or {}
    admin_id = session.get('user_id')
    result, status_code = TaskService.update_task(task_id, data, admin_id)
    return jsonify(result), status_code

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@admin_required
def delete_task(task_id):
    """Soft delete a task (Admin only)."""
    admin_id = session.get('user_id')
    result, status_code = TaskService.soft_delete_task(task_id, admin_id)
    return jsonify(result), status_code
