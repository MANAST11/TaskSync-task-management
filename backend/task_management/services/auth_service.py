from datetime import datetime
from flask import session
from task_management.extensions import db
from task_management.models import User, Employee
from task_management.services.activity_service import ActivityService

class AuthService:
    @staticmethod
    def login_user(username, password):
        """Authenticate user credentials and initialize session."""
        if not username or not password:
            return {"error": "Username and password are required"}, 400
            
        user = User.query.filter_by(username=username).first()
        
        if not user or user.status == 'inactive' or not user.check_password(password):
            return {"error": "Invalid username, password, or account is disabled"}, 401
            
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Populate session variables
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        # Log action
        ActivityService.log_activity(
            user_id=user.id,
            action="LOGIN",
            description=f"User {user.username} successfully logged in."
        )
        
        # Prepare response profile
        response_data = {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
        
        # Include employee information if applicable
        if user.role == 'employee' and user.employee_profile:
            response_data["employee_id"] = user.employee_profile.id
            response_data["first_name"] = user.employee_profile.first_name
            response_data["last_name"] = user.employee_profile.last_name
            
        return {"message": "Login successful", "user": response_data}, 200

    @staticmethod
    def logout_user():
        """Terminate current user session."""
        user_id = session.get('user_id')
        username = session.get('username')
        
        if user_id:
            ActivityService.log_activity(
                user_id=user_id,
                action="LOGOUT",
                description=f"User {username} logged out."
            )
            
        session.clear()
        return {"message": "Logout successful"}, 200

    @staticmethod
    def get_current_user(user_id):
        """Retrieve complete details of the currently logged-in user."""
        user = User.query.get(user_id)
        if not user or user.status == 'inactive':
            return {"error": "User session invalid or inactive"}, 401
            
        user_data = user.to_dict()
        
        if user.role == 'employee':
            employee = Employee.query.filter_by(user_id=user.id).first()
            if employee:
                user_data['employee_details'] = employee.to_dict()
                
        return {"user": user_data}, 200
