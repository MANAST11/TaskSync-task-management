from functools import wraps
from flask import session, jsonify

def login_required(f):
    """Decorator to restrict route access to authenticated users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to restrict route access to administrators only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        if session.get('role') != 'administrator':
            return jsonify({"error": "Forbidden. Administrator access required."}), 403
        return f(*args, **kwargs)
    return decorated_function
