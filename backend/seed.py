import os
import sys

# Ensure backend directory is in the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from task_management import create_app
from task_management.extensions import db
from task_management.models import User, Department, Employee, Task, TaskAssignment, ActivityLog

app = create_app()

def seed_database():
    with app.app_context():
        # Clear existing tables if they exist
        db.drop_all()
        db.create_all()

        print("Database schema generated successfully.")

        # 1. Seed Departments
        eng = Department(name="Engineering", description="Software development, QA, and infrastructure management.")
        hr = Department(name="Human Resources", description="Recruitment, onboarding, employee relations, and culture.")
        prod = Department(name="Product Management", description="Product strategy, roadmap development, and user research.")
        mktg = Department(name="Marketing", description="Digital marketing, campaigns, branding, and content creation.")
        
        db.session.add_all([eng, hr, prod, mktg])
        db.session.flush() # Populate IDs

        # 2. Seed Admin User
        admin = User(username="admin", role="administrator", status="active")
        admin.set_password("password123")
        db.session.add(admin)

        # 3. Seed Employee Users
        jdoe_user = User(username="jdoe", role="employee", status="active")
        jdoe_user.set_password("password123")
        
        asmith_user = User(username="asmith", role="employee", status="active")
        asmith_user.set_password("password123")
        
        mwilliams_user = User(username="mwilliams", role="employee", status="active")
        mwilliams_user.set_password("password123")

        db.session.add_all([jdoe_user, asmith_user, mwilliams_user])
        db.session.flush() # Populate IDs

        # 4. Seed Employee Profiles
        jdoe_emp = Employee(
            user_id=jdoe_user.id,
            first_name="John",
            last_name="Doe",
            email="john.doe@organization.org",
            phone="+15550101",
            department_id=eng.id,
            designation="Senior Backend Engineer"
        )
        
        asmith_emp = Employee(
            user_id=asmith_user.id,
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@organization.org",
            phone="+15550102",
            department_id=eng.id,
            designation="QA Automation Engineer"
        )
        
        mwilliams_emp = Employee(
            user_id=mwilliams_user.id,
            first_name="Mark",
            last_name="Williams",
            email="mark.williams@organization.org",
            phone="+15550103",
            department_id=prod.id,
            designation="Product Owner"
        )

        db.session.add_all([jdoe_emp, asmith_emp, mwilliams_emp])
        db.session.flush()

        # 5. Seed Tasks
        t1 = Task(title="Implement JWT Auth", description="Create JWT-based secure authentication routes for external clients.", priority="high", estimated_hours=16.0, created_by=admin.id)
        t2 = Task(title="Database Indexing", description="Optimize tasks and activity logs query performance using indexing.", priority="medium", estimated_hours=8.0, created_by=admin.id)
        t3 = Task(title="Redesign Login UI", description="Create a modern, sleek glassmorphic login screen for the frontend.", priority="low", estimated_hours=12.0, created_by=admin.id)
        t4 = Task(title="Draft Product Roadmap", description="Outline Q3 feature releases and resource allocations.", priority="high", estimated_hours=20.0, created_by=admin.id)

        db.session.add_all([t1, t2, t3, t4])
        db.session.flush()

        # 6. Seed Assignments
        a1 = TaskAssignment(task_id=t1.id, employee_id=jdoe_emp.id, status="in_progress", completion_percentage=50, remarks="Auth middleware created, implementing route tests.")
        a2 = TaskAssignment(task_id=t2.id, employee_id=asmith_emp.id, status="pending", completion_percentage=0)
        a3 = TaskAssignment(task_id=t3.id, employee_id=asmith_emp.id, status="completed", completion_percentage=100, remarks="UI designed, integrated with frontend API client.")
        a4 = TaskAssignment(task_id=t4.id, employee_id=mwilliams_emp.id, status="in_progress", completion_percentage=25, remarks="Discussed goals with stakeholders, draft in progress.")

        db.session.add_all([a1, a2, a3, a4])

        # 7. Seed Initial System logs
        log1 = ActivityLog(user_id=admin.id, action="USER_CREATION", description="Created admin account during initial setup.")
        log2 = ActivityLog(user_id=admin.id, action="EMPLOYEE_CREATION", description="Created employee profile for John Doe.")
        log3 = ActivityLog(user_id=admin.id, action="TASK_CREATION", description="Created task: Implement JWT Auth.")
        log4 = ActivityLog(user_id=admin.id, action="TASK_ASSIGNMENT", description="Assigned task Implement JWT Auth to John Doe.")

        db.session.add_all([log1, log2, log3, log4])

        db.session.commit()
        print("Database seeded with sample data successfully!")

if __name__ == '__main__':
    seed_database()
