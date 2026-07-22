import re
from task_management.extensions import db
from task_management.models import User, Employee, Department
from task_management.services.activity_service import ActivityService

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class EmployeeService:
    @staticmethod
    def get_all_employees():
        """Retrieve all employees along with their user credential details."""
        employees = Employee.query.all()
        return [e.to_dict() for e in employees], 200

    @staticmethod
    def create_employee(data, admin_user_id):
        """Create a User and corresponding Employee profile transactionally."""
        username = data.get('username', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        department_id = data.get('department_id')
        designation = data.get('designation', '').strip()

        # Validation
        if not all([username, password, first_name, last_name, email]):
            return {"error": "Missing required fields (username, password, first_name, last_name, email)"}, 400

        if not re.match(EMAIL_REGEX, email):
            return {"error": "Invalid email address format"}, 400

        # Unique Checks
        if User.query.filter_by(username=username).first():
            return {"error": "Username already taken"}, 409

        if Employee.query.filter_by(email=email).first():
            return {"error": "Email already registered"}, 409

        if department_id:
            dept = Department.query.get(department_id)
            if not dept:
                return {"error": "Department not found"}, 404

        try:
            # 1. Create authentication User
            new_user = User(username=username, role='employee', status='active')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush() # Populate new_user.id for FK association

            # 2. Create Employee profile
            new_employee = Employee(
                user_id=new_user.id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                department_id=department_id,
                designation=designation
            )
            db.session.add(new_employee)
            db.session.commit()

            # Log action
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="EMPLOYEE_CREATION",
                description=f"Created employee profile for {first_name} {last_name} (username: {username})."
            )

            return {"message": "Employee created successfully", "employee": new_employee.to_dict()}, 201

        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    @staticmethod
    def update_employee(employee_id, data, admin_user_id):
        """Update employee profile and linked user account details."""
        employee = Employee.query.get(employee_id)
        if not employee:
            return {"error": "Employee not found"}, 404

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        department_id = data.get('department_id')
        designation = data.get('designation')
        status = data.get('status') # active or inactive
        password = data.get('password') # optional password reset

        try:
            # Update employee details if provided
            if first_name is not None:
                employee.first_name = first_name.strip()
            if last_name is not None:
                employee.last_name = last_name.strip()
            if email is not None:
                email = email.strip()
                if not re.match(EMAIL_REGEX, email):
                    return {"error": "Invalid email address format"}, 400
                existing = Employee.query.filter_by(email=email).first()
                if existing and existing.id != employee.id:
                    return {"error": "Email is already in use by another employee"}, 409
                employee.email = email
            if phone is not None:
                employee.phone = phone.strip()
            if designation is not None:
                employee.designation = designation.strip()
                
            if department_id is not None:
                if department_id == "" or department_id is None:
                    employee.department_id = None
                else:
                    dept = Department.query.get(department_id)
                    if not dept:
                        return {"error": "Department not found"}, 404
                    employee.department_id = department_id

            # Update associated User fields
            user = employee.user
            if user:
                if status in ['active', 'inactive']:
                    user.status = status
                if password and password.strip():
                    user.set_password(password)

            db.session.commit()

            # Log action
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="EMPLOYEE_UPDATE",
                description=f"Updated employee profile for ID {employee.id} ({employee.first_name} {employee.last_name})."
            )

            return {"message": "Employee updated successfully", "employee": employee.to_dict()}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    @staticmethod
    def delete_employee(employee_id, admin_user_id):
        """Remove employee profile and cascade to delete their user account."""
        employee = Employee.query.get(employee_id)
        if not employee:
            return {"error": "Employee not found"}, 404

        user = employee.user
        emp_name = f"{employee.first_name} {employee.last_name}"

        try:
            # Deleting user will cascade delete employee due to ON DELETE CASCADE
            if user:
                db.session.delete(user)
            else:
                db.session.delete(employee)
            db.session.commit()

            # Log action
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="EMPLOYEE_DELETION",
                description=f"Deleted employee {emp_name} (ID: {employee_id})."
            )

            return {"message": f"Employee {emp_name} deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
