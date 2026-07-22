from sqlalchemy import func
from task_management.extensions import db
from task_management.models import Task, Employee, Department, TaskAssignment, ActivityLog

class DashboardService:
    @staticmethod
    def get_admin_stats():
        """Retrieve aggregated statistics for the administrator dashboard."""
        # 1. Basic entity counts
        total_tasks = Task.query.filter_by(is_deleted=False).count()
        total_employees = Employee.query.count()
        total_departments = Department.query.count()

        # 2. Task Assignment status counts
        status_counts = db.session.query(
            TaskAssignment.status, func.count(TaskAssignment.id)
        ).join(Task).filter(Task.is_deleted == False).group_by(TaskAssignment.status).all()
        
        status_map = {'pending': 0, 'in_progress': 0, 'completed': 0}
        for status, count in status_counts:
            if status in status_map:
                status_map[status] = count

        # 3. Task Priority Distribution
        priority_counts = db.session.query(
            Task.priority, func.count(Task.id)
        ).filter(Task.is_deleted == False).group_by(Task.priority).all()
        
        priority_map = {'low': 0, 'medium': 0, 'high': 0}
        for priority, count in priority_counts:
            if priority in priority_map:
                priority_map[priority] = count

        # 4. Department-wise task/employee distributions
        dept_distributions = []
        departments = Department.query.all()
        for dept in departments:
            emp_count = Employee.query.filter_by(department_id=dept.id).count()
            # Count tasks assigned to employees in this department
            assigned_tasks_count = TaskAssignment.query.join(Employee).filter(
                Employee.department_id == dept.id
            ).join(Task).filter(Task.is_deleted == False).distinct(TaskAssignment.task_id).count()
            
            dept_distributions.append({
                'department_id': dept.id,
                'department_name': dept.name,
                'employee_count': emp_count,
                'task_count': assigned_tasks_count
            })

        # 5. Recent Assignments (last 5)
        recent_assignments = TaskAssignment.query.join(Task).filter(
            Task.is_deleted == False
        ).order_by(TaskAssignment.assigned_at.desc()).limit(5).all()

        # 6. Recent Activity Logs (last 10)
        recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()

        return {
            "counts": {
                "tasks": total_tasks,
                "employees": total_employees,
                "departments": total_departments,
                "assignments_pending": status_map['pending'],
                "assignments_in_progress": status_map['in_progress'],
                "assignments_completed": status_map['completed']
            },
            "status_distribution": status_map,
            "priority_distribution": priority_map,
            "department_stats": dept_distributions,
            "recent_assignments": [ra.to_dict() for ra in recent_assignments],
            "recent_activities": [rl.to_dict() for rl in recent_logs]
        }, 200

    @staticmethod
    def get_employee_stats(employee_id):
        """Retrieve aggregated statistics for a specific employee's dashboard."""
        # 1. Retrieve all assignments of the employee where the task is not deleted
        assignments = TaskAssignment.query.join(Task).filter(
            TaskAssignment.employee_id == employee_id,
            Task.is_deleted == False
        ).all()

        total_assigned = len(assignments)
        
        status_map = {'pending': 0, 'in_progress': 0, 'completed': 0}
        total_estimated_hours = 0.0
        completed_hours = 0.0

        for a in assignments:
            status_map[a.status] = status_map.get(a.status, 0) + 1
            hours = float(a.task.estimated_hours) if a.task.estimated_hours else 0.0
            total_estimated_hours += hours
            if a.status == 'completed':
                completed_hours += hours
            elif a.status == 'in_progress':
                completed_hours += hours * (a.completion_percentage / 100.0)

        progress_overall = 0
        if total_assigned > 0:
            progress_overall = int(sum(a.completion_percentage for a in assignments) / total_assigned)

        return {
            "total_assigned": total_assigned,
            "pending": status_map['pending'],
            "in_progress": status_map['in_progress'],
            "completed": status_map['completed'],
            "completion_percentage": progress_overall,
            "total_estimated_hours": total_estimated_hours,
            "completed_hours": round(completed_hours, 2)
        }, 200
