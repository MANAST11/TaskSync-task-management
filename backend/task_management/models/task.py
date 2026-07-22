from datetime import datetime
from task_management.extensions import db

class Task(db.Model):
    """Task Definition Model."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Enum('low', 'medium', 'high', name='task_priorities'), nullable=False, default='medium')
    estimated_hours = db.Column(db.Numeric(5, 2), nullable=False, default=0.00)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, index=True)

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    assignments = db.relationship('TaskAssignment', back_populates='task', cascade="all, delete-orphan", lazy=True)

    def to_dict(self, include_assignments=False):
        """Serialize Task object into dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'estimated_hours': float(self.estimated_hours) if self.estimated_hours else 0.0,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }
        if include_assignments:
            data['assignments'] = [a.to_dict() for a in self.assignments]
        return data
