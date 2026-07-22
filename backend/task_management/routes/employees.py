from flask import Blueprint, request, jsonify, session
from task_management.services.employee_service import EmployeeService
from task_management.utils.auth_helpers import admin_required

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
@admin_required
def get_employees():
    """Retrieve all employees."""
    result, status_code = EmployeeService.get_all_employees()
    return jsonify(result), status_code

@employees_bp.route('/employees', methods=['POST'])
@admin_required
def create_employee():
    """Create a new employee profile and account."""
    data = request.get_json() or {}
    admin_id = session.get('user_id')
    result, status_code = EmployeeService.create_employee(data, admin_id)
    return jsonify(result), status_code

@employees_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@admin_required
def update_employee(employee_id):
    """Update employee details and status."""
    data = request.get_json() or {}
    admin_id = session.get('user_id')
    result, status_code = EmployeeService.update_employee(employee_id, data, admin_id)
    return jsonify(result), status_code

@employees_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@admin_required
def delete_employee(employee_id):
    """Delete an employee and their user account."""
    admin_id = session.get('user_id')
    result, status_code = EmployeeService.delete_employee(employee_id, admin_id)
    return jsonify(result), status_code
