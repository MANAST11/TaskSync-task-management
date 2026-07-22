from flask import Blueprint, request, jsonify, session
from task_management.services.auth_service import AuthService
from task_management.utils.auth_helpers import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Route for user login authentication."""
    # Handle incoming JSON request data
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    result, status_code = AuthService.login_user(username, password)
    return jsonify(result), status_code

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Route for user logout and session termination."""
    result, status_code = AuthService.logout_user()
    return jsonify(result), status_code

@auth_bp.route('/current-user', methods=['GET'])
@login_required
def current_user():
    """Route to fetch current authenticated user profile."""
    user_id = session.get('user_id')
    result, status_code = AuthService.get_current_user(user_id)
    return jsonify(result), status_code
