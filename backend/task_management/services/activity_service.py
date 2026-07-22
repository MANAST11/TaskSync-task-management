from task_management.extensions import db
from task_management.models import ActivityLog

class ActivityService:
    @staticmethod
    def log_activity(user_id, action, description):
        """Helper to create audit trails in activity_logs."""
        try:
            log = ActivityLog(user_id=user_id, action=action, description=description)
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            # Log error locally but do not crash the request
            print(f"Failed to write activity log: {str(e)}")
            return None

    @staticmethod
    def get_all_logs(limit=100):
        """Retrieve recent system logs ordered by creation date."""
        return ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
