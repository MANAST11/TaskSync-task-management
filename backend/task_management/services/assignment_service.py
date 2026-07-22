from task_management.extensions import db
from task_management.models import Task, Employee, TaskAssignment
from task_management.services.activity_service import ActivityService

class AssignmentService:
    @staticmethod
    def assign_task(task_id, employee_id, admin_user_id):
        """Assign a task to an employee."""
        if not task_id or not employee_id:
            return {"error": "Both task_id and employee_id are required"}, 400

        task = Task.query.filter(Task.id == task_id, Task.is_deleted == False).first()
        if not task:
            return {"error": "Task not found or has been deleted"}, 404

        employee = Employee.query.get(employee_id)
        if not employee:
            return {"error": "Employee not found"}, 404

        if employee.user and employee.user.status != 'active':
            return {"error": "Cannot assign tasks to an inactive employee"}, 400

        # Check existing assignment
        existing = TaskAssignment.query.filter_by(task_id=task_id, employee_id=employee_id).first()
        if existing:
            return {"error": "Task is already assigned to this employee"}, 409

        try:
            assignment = TaskAssignment(
                task_id=task_id,
                employee_id=employee_id,
                status='pending',
                completion_percentage=0
            )
            db.session.add(assignment)
            db.session.commit()

            # Log activity
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="TASK_ASSIGNMENT",
                description=f"Assigned task '{task.title}' (ID: {task_id}) to employee {employee.first_name} {employee.last_name} (ID: {employee_id})."
            )

            return {"message": "Task assigned successfully", "assignment": assignment.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    @staticmethod
    def update_assignment(assignment_id, data, user_id, role, employee_id=None):
        """Update assignment status, progress, and remarks."""
        assignment = TaskAssignment.query.get(assignment_id)
        if not assignment:
            return {"error": "Assignment not found"}, 404

        # Authorization: Employees can only update their own assignments
        if role == 'employee' and assignment.employee_id != employee_id:
            return {"error": "Access denied. You cannot modify assignments for other employees."}, 403

        status = data.get('status')
        completion_percentage = data.get('completion_percentage')
        remarks = data.get('remarks')

        try:
            # 1. Update Remarks
            if remarks is not None:
                assignment.remarks = remarks.strip()

            # 2. Update Progress Percentage
            if completion_percentage is not None:
                try:
                    pct = int(completion_percentage)
                    if pct < 0 or pct > 100:
                        return {"error": "Completion percentage must be between 0 and 100"}, 400
                    assignment.completion_percentage = pct
                    
                    # Auto-set status based on percentage
                    if pct == 100:
                        assignment.status = 'completed'
                    elif pct > 0 and assignment.status == 'pending':
                        assignment.status = 'in_progress'
                except ValueError:
                    return {"error": "Completion percentage must be an integer"}, 400

            # 3. Update Status
            if status is not None:
                if status not in ['pending', 'in_progress', 'completed']:
                    return {"error": "Invalid status. Use 'pending', 'in_progress', or 'completed'."}, 400
                assignment.status = status
                
                # Auto-adjust completion percentage based on status
                if status == 'completed':
                    assignment.completion_percentage = 100
                elif status == 'pending':
                    assignment.completion_percentage = 0
                elif status == 'in_progress' and assignment.completion_percentage == 100:
                    # Reset if moving back to in_progress from completed
                    assignment.completion_percentage = 90

            db.session.commit()

            # Log activity
            actor_name = "Administrator" if role == 'administrator' else f"Employee (ID: {employee_id})"
            ActivityService.log_activity(
                user_id=user_id,
                action="ASSIGNMENT_UPDATE",
                description=f"{actor_name} updated assignment ID {assignment_id} (Task: '{assignment.task.title}'). Status: {assignment.status}, Completion: {assignment.completion_percentage}%."
            )

            return {"message": "Assignment updated successfully", "assignment": assignment.to_dict()}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    @staticmethod
    def get_employee_assignments(target_employee_id, user_id, role, current_employee_id=None):
        """Retrieve task list for a specific employee."""
        # Employees can only query their own ID
        if role == 'employee' and target_employee_id != current_employee_id:
            return {"error": "Access denied. Cannot retrieve other employees' assignments."}, 403

        employee = Employee.query.get(target_employee_id)
        if not employee:
            return {"error": "Employee not found"}, 404

        # Query assignments where the task is not soft deleted
        assignments = TaskAssignment.query.join(Task).filter(
            TaskAssignment.employee_id == target_employee_id,
            Task.is_deleted == False
        ).order_by(TaskAssignment.assigned_at.desc()).all()

        return [a.to_dict() for a in assignments], 200
