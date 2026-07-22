-- Sample Data for Task Management System
USE task_management_db;

-- 1. Insert Departments
INSERT INTO departments (name, description) VALUES
('Engineering', 'Software development, QA, and infrastructure management.'),
('Human Resources', 'Recruitment, onboarding, employee relations, and culture.'),
('Product Management', 'Product strategy, roadmap development, and user research.'),
('Marketing', 'Digital marketing, campaigns, branding, and content creation.');

-- 2. Insert Users (Passwords are hashed values of 'password123')
-- Hash for 'password123' using pbkdf2:sha256 (may differ by system, python seeder is recommended for actual deployment)
INSERT INTO users (username, password_hash, role, status) VALUES
('admin', 'scrypt:32768:8:1$kFvTzQcE$e3d9370020bc8b60bb4d156543b59df56214cdab964e5c5fa905ea58ce1f0d36746cf617a77f3e82d02c89280d4f3925c4efbe99f4d7b57b545dcd5a89467610', 'administrator', 'active'),
('jdoe', 'scrypt:32768:8:1$kFvTzQcE$e3d9370020bc8b60bb4d156543b59df56214cdab964e5c5fa905ea58ce1f0d36746cf617a77f3e82d02c89280d4f3925c4efbe99f4d7b57b545dcd5a89467610', 'employee', 'active'),
('asmith', 'scrypt:32768:8:1$kFvTzQcE$e3d9370020bc8b60bb4d156543b59df56214cdab964e5c5fa905ea58ce1f0d36746cf617a77f3e82d02c89280d4f3925c4efbe99f4d7b57b545dcd5a89467610', 'employee', 'active'),
('mwilliams', 'scrypt:32768:8:1$kFvTzQcE$e3d9370020bc8b60bb4d156543b59df56214cdab964e5c5fa905ea58ce1f0d36746cf617a77f3e82d02c89280d4f3925c4efbe99f4d7b57b545dcd5a89467610', 'employee', 'active');

-- 3. Insert Employees
INSERT INTO employees (user_id, first_name, last_name, email, phone, department_id, designation) VALUES
(2, 'John', 'Doe', 'john.doe@organization.org', '+15550101', 1, 'Senior Backend Engineer'),
(3, 'Alice', 'Smith', 'alice.smith@organization.org', '+15550102', 1, 'QA Automation Engineer'),
(4, 'Mark', 'Williams', 'mark.williams@organization.org', '+15550103', 3, 'Product Owner');

-- 4. Insert Tasks
INSERT INTO tasks (title, description, priority, estimated_hours, created_by) VALUES
('Implement JWT Auth', 'Create JWT-based secure authentication routes for external clients.', 'high', 16.00, 1),
('Database Indexing', 'Optimize tasks and activity logs query performance using indexing.', 'medium', 8.00, 1),
('Redesign Login UI', 'Create a modern, sleek glassmorphic login screen for the frontend.', 'low', 12.00, 1),
('Draft Product Roadmap', 'Outline Q3 feature releases and resource allocations.', 'high', 20.00, 1);

-- 5. Insert Task Assignments
INSERT INTO task_assignments (task_id, employee_id, status, completion_percentage, remarks) VALUES
(1, 1, 'in_progress', 50, 'Auth middleware created, implementing route tests.'),
(2, 2, 'pending', 0, NULL),
(3, 2, 'completed', 100, 'UI designed, integrated with frontend API client.'),
(4, 3, 'in_progress', 25, 'Discussed goals with stakeholders, draft in progress.');

-- 6. Insert Activity Logs
INSERT INTO activity_logs (user_id, action, description) VALUES
(1, 'USER_CREATION', 'Created admin account during initial setup.'),
(1, 'EMPLOYEE_CREATION', 'Created employee profile for John Doe.'),
(1, 'TASK_CREATION', 'Created task: Implement JWT Auth.'),
(1, 'TASK_ASSIGNMENT', 'Assigned task Implement JWT Auth to employee John Doe.');
