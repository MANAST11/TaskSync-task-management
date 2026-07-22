from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from task_management.extensions import db

class User(db.Model):
    """User Credentials and Session Model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('administrator', 'employee', name='user_roles'), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', name='user_statuses'), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    employee_profile = db.relationship('Employee', back_populates='user', uselist=False, cascade="all, delete-orphan")
    activity_logs = db.relationship('ActivityLog', back_populates='user', lazy=True)

    def set_password(self, password):
        """Hash and set user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize User object into dictionary, redacting sensitive fields."""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
