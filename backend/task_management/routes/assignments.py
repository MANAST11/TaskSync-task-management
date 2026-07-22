from flask import Blueprint, request, jsonify, session
from task_management.services.assignment_service import AssignmentService
from task_management.utils.auth_helpers import login_required, admin_required

assignments_bp = Blueprint('assignments', __name__)

@assignments_bp.route('/assign', methods=['POST'])
@admin_required
def assign_task():
    """Assign a task to an employee (Admin only)."""
    data = request.get_json() or {}
    task_id = data.get('task_id')
    employee_id = data.get('employee_id')
    
    admin_id = session.get('user_id')
    result, status_code = AssignmentService.assign_task(task_id, employee_id, admin_id)
    return jsonify(result), status_code

@assignments_bp.route('/assignment/<int:assignment_id>', methods=['PUT'])
@login_required
def update_assignment(assignment_id):
    """Update progress status, completion, and remarks of an assignment."""
    data = request.get_json() or {}
    user_id = session.get('user_id')
    role = session.get('role')
    
    employee_id = None
    if role == 'employee':
        from task_management.models import Employee
        emp = Employee.query.filter_by(user_id=user_id).first()
        if emp:
            employee_id = emp.id

    result, status_code = AssignmentService.update_assignment(assignment_id, data, user_id, role, employee_id)
    return jsonify(result), status_code

@assignments_bp.route('/employee/<int:employee_id>/tasks', methods=['GET'])
@login_required
def get_employee_tasks(employee_id):
    """Retrieve all assigned tasks for a given employee ID."""
    user_id = session.get('user_id')
    role = session.get('role')
    
    current_employee_id = None
    if role == 'employee':
        from task_management.models import Employee
        emp = Employee.query.filter_by(user_id=user_id).first()
        if emp:
            current_employee_id = emp.id

    result, status_code = AssignmentService.get_employee_assignments(employee_id, user_id, role, current_employee_id)
    return jsonify(result), status_code
