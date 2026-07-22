from flask import Blueprint, jsonify, session
from task_management.services.dashboard_service import DashboardService
from task_management.services.activity_service import ActivityService
from task_management.utils.auth_helpers import login_required, admin_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Retrieve dashboard statistics. Returns admin or employee stats based on user role."""
    user_id = session.get('user_id')
    role = session.get('role')
    
    if role == 'administrator':
        result, status_code = DashboardService.get_admin_stats()
        return jsonify(result), status_code
        
    elif role == 'employee':
        from task_management.models import Employee
        emp = Employee.query.filter_by(user_id=user_id).first()
        if not emp:
            return jsonify({"error": "Employee profile not found"}), 404
            
        result, status_code = DashboardService.get_employee_stats(emp.id)
        return jsonify(result), status_code

    return jsonify({"error": "Invalid user role"}), 400

@dashboard_bp.route('/activity-logs', methods=['GET'])
@admin_required
def get_activity_logs():
    """Retrieve recent system activity logs (Admin only)."""
    logs = ActivityService.get_all_logs(limit=100)
    return jsonify([log.to_dict() for log in logs]), 200
