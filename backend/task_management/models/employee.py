from task_management.extensions import db

class Employee(db.Model):
    """Employee Details Model."""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    designation = db.Column(db.String(100), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='employee_profile')
    department = db.relationship('Department', back_populates='employees')
    assignments = db.relationship('TaskAssignment', back_populates='employee', cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        """Serialize Employee object into dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'designation': self.designation,
            'username': self.user.username if self.user else None,
            'status': self.user.status if self.user else None
        }
