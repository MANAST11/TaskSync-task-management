from flask import Blueprint, request, jsonify, session
from task_management.services.department_service import DepartmentService
from task_management.utils.auth_helpers import login_required, admin_required

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/departments', methods=['GET'])
@login_required
def get_departments():
    """Retrieve all departments list."""
    result, status_code = DepartmentService.get_all_departments()
    return jsonify(result), status_code

@departments_bp.route('/departments', methods=['POST'])
@admin_required
def create_department():
    """Create a new department."""
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    
    admin_id = session.get('user_id')
    result, status_code = DepartmentService.create_department(name, description, admin_id)
    return jsonify(result), status_code
