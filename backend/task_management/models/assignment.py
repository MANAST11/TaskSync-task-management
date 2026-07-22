from datetime import datetime
from task_management.extensions import db

class TaskAssignment(db.Model):
    """Task Assignment Join Model."""
    __tablename__ = 'task_assignments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', name='assignment_statuses'), nullable=False, default='pending')
    completion_percentage = db.Column(db.Integer, nullable=False, default=0)
    remarks = db.Column(db.Text, nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        db.UniqueConstraint('task_id', 'employee_id', name='unique_task_employee'),
    )

    # Relationships
    task = db.relationship('Task', back_populates='assignments')
    employee = db.relationship('Employee', back_populates='assignments')

    def to_dict(self):
        """Serialize TaskAssignment object into dictionary."""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': self.task.title if self.task else None,
            'task_description': self.task.description if self.task else None,
            'task_priority': self.task.priority if self.task else None,
            'task_estimated_hours': float(self.task.estimated_hours) if self.task and self.task.estimated_hours else 0.0,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}" if self.employee else None,
            'employee_email': self.employee.email if self.employee else None,
            'status': self.status,
            'completion_percentage': self.completion_percentage,
            'remarks': self.remarks,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
