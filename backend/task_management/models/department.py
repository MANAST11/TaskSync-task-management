from task_management.extensions import db

class Department(db.Model):
    """Department Model for SQL database."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    employees = db.relationship('Employee', back_populates='department', lazy=True)

    def to_dict(self, include_employees=False):
        """Serialize Department object into dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        if include_employees:
            data['employees'] = [e.to_dict() for e in self.employees]
        return data
