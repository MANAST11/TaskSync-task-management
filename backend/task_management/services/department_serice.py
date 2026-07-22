from task_management.extensions import db
from task_management.models import Department
from task_management.services.activity_service import ActivityService

class DepartmentService:
    @staticmethod
    def get_all_departments():
        """Retrieve all departments from the database."""
        departments = Department.query.order_by(Department.name.asc()).all()
        return [d.to_dict() for d in departments], 200

    @staticmethod
    def create_department(name, description, admin_user_id):
        """Create a new department after checking unique constraints."""
        if not name or not name.strip():
            return {"error": "Department name is required"}, 400
            
        name = name.strip()
        existing = Department.query.filter_by(name=name).first()
        if existing:
            return {"error": f"Department with name '{name}' already exists"}, 409
            
        try:
            dept = Department(name=name, description=description)
            db.session.add(dept)
            db.session.commit()
            
            # Log action
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="DEPARTMENT_CREATION",
                description=f"Created department '{dept.name}'."
            )
            
            return {"message": "Department created successfully", "department": dept.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
