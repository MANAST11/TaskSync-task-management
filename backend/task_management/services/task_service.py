from sqlalchemy import or_, desc, asc
from task_management.extensions import db
from task_management.models import Task, TaskAssignment, Employee
from task_management.services.activity_service import ActivityService

class TaskService:
    @staticmethod
    def get_tasks(filters, user_id, role, employee_id=None):
        """Retrieve tasks with optional filters, pagination, search, and sorting."""
        # 1. Base Query - filter out soft deleted tasks
        query = Task.query.filter(Task.is_deleted == False)

        # 2. Scope restriction: Employees can only see tasks assigned to them
        if role == 'employee':
            if not employee_id:
                return {"error": "Employee profile required for this operation"}, 403
            query = query.join(TaskAssignment).filter(TaskAssignment.employee_id == employee_id)
        elif filters.get('employee_id'):
            # Admin filtering by employee ID
            query = query.join(TaskAssignment).filter(TaskAssignment.employee_id == filters.get('employee_id'))

        # 3. Apply Search (Title / Description)
        search_query = filters.get('search', '').strip()
        if search_query:
            query = query.filter(
                or_(
                    Task.title.ilike(f"%{search_query}%"),
                    Task.description.ilike(f"%{search_query}%")
                )
            )

        # 4. Apply Filters
        priority = filters.get('priority')
        if priority in ['low', 'medium', 'high']:
            query = query.filter(Task.priority == priority)

        status = filters.get('status')
        if status in ['pending', 'in_progress', 'completed']:
            if role != 'employee' and not filters.get('employee_id'):
                # General query join if not already joined
                query = query.join(TaskAssignment).filter(TaskAssignment.status == status)
            else:
                # Already joined or employee profile active
                query = query.filter(TaskAssignment.status == status)

        # 5. Sorting
        sort_by = filters.get('sort_by', 'created_at')
        sort_dir = filters.get('sort_dir', 'desc')
        
        column = getattr(Task, sort_by, Task.created_at)
        if sort_dir == 'asc':
            query = query.order_by(asc(column))
        else:
            query = query.order_by(desc(column))

        # 6. Pagination
        try:
            page = int(filters.get('page', 1))
            limit = int(filters.get('limit', 10))
        except ValueError:
            page = 1
            limit = 10

        paginated_obj = query.paginate(page=page, per_page=limit, error_out=False)

        # Format output
        tasks_list = []
        for task in paginated_obj.items:
            task_dict = task.to_dict(include_assignments=True)
            # If scoped to single employee, extract specific status
            if role == 'employee' and employee_id:
                assignment = next((a for a in task.assignments if a.employee_id == employee_id), None)
                if assignment:
                    task_dict['assignment_status'] = assignment.status
                    task_dict['completion_percentage'] = assignment.completion_percentage
                    task_dict['remarks'] = assignment.remarks
                    task_dict['assignment_id'] = assignment.id
            tasks_list.append(task_dict)

        return {
            "tasks": tasks_list,
            "total": paginated_obj.total,
            "pages": paginated_obj.pages,
            "current_page": paginated_obj.page,
            "limit": limit
        }, 200

    @staticmethod
    def get_task_by_id(task_id, user_id, role, employee_id=None):
        """Fetch details of a single task, checking employee assignment permissions."""
        task = Task.query.filter(Task.id == task_id, Task.is_deleted == False).first()
        if not task:
            return {"error": "Task not found"}, 404

        if role == 'employee':
            assignment = TaskAssignment.query.filter_by(task_id=task_id, employee_id=employee_id).first()
            if not assignment:
                return {"error": "Access denied. Task is not assigned to you."}, 403

        return {"task": task.to_dict(include_assignments=True)}, 200

    @staticmethod
    def create_task(data, admin_user_id):
        """Create a new task."""
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        priority = data.get('priority', 'medium')
        estimated_hours = data.get('estimated_hours', 0.0)

        if not title:
            return {"error": "Task title is required"}, 400

        if priority not in ['low', 'medium', 'high']:
            return {"error": "Invalid priority level. Use 'low', 'medium', or 'high'."}, 400

        try:
            estimated_hours = float(estimated_hours)
            if estimated_hours < 0:
                return {"error": "Estimated hours cannot be negative"}, 400
        except (ValueError, TypeError):
            return {"error": "Invalid value for estimated hours"}, 400

        try:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                estimated_hours=estimated_hours,
                created_by=admin_user_id
            )
            db.session.add(task)
            db.session.commit()

            # Log activity
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="TASK_CREATION",
                description=f"Created task '{title}' (ID: {task.id})."
            )

            return {"message": "Task created successfully", "task": task.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    @staticmethod
    def update_task(task_id, data, admin_user_id):
        """Update a task's parameters."""
        task = Task.query.filter(Task.id == task_id, Task.is_deleted == False).first()
        if not task:
            return {"error": "Task not found"}, 404

        title = data.get('title')
        description = data.get('description')
        priority = data.get('priority')
        estimated_hours = data.get('estimated_hours')

        try:
            if title is not None:
                if not title.strip():
                    return {"error": "Title cannot be empty"}, 400
                task.title = title.strip()
            if description is not None:
                task.description = description.strip()
            if priority is not None:
                if priority not in ['low', 'medium', 'high']:
                    return {"error": "Invalid priority level"}, 400
                task.priority = priority
            if estimated_hours is not None:
                task.estimated_hours = float(estimated_hours)
                if task.estimated_hours < 0:
                    return {"error": "Estimated hours cannot be negative"}, 400

            db.session.commit()

            # Log activity
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="TASK_UPDATE",
                description=f"Updated details for task '{task.title}' (ID: {task.id})."
            )

            return {"message": "Task updated successfully", "task": task.to_dict()}, 200
        except ValueError:
            return {"error": "Invalid value for estimated hours"}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    @staticmethod
    def soft_delete_task(task_id, admin_user_id):
        """Mark a task as deleted (soft delete)."""
        task = Task.query.filter(Task.id == task_id, Task.is_deleted == False).first()
        if not task:
            return {"error": "Task not found"}, 404

        try:
            task.is_deleted = True
            db.session.commit()

            # Log activity
            ActivityService.log_activity(
                user_id=admin_user_id,
                action="TASK_DELETION",
                description=f"Soft deleted task '{task.title}' (ID: {task_id})."
            )

            return {"message": f"Task '{task.title}' soft-deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
