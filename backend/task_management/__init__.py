import os
from flask import Flask, jsonify
from task_management.config import config_by_name
from task_management.extensions import db, cors, session_manager

def create_app(config_name=None):
    """Application factory for Task Management Backend."""
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    app = Flask(__name__)
    
    # Load configuration
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)
    
    # Ensure folders for filesystem sessions exist if needed
    if app.config.get('SESSION_TYPE') == 'filesystem':
        os.makedirs(app.config.get('SESSION_FILE_DIR'), exist_ok=True)
        
    # Initialize Extensions
    db.init_app(app)
    cors.init_app(app, supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8000", "http://localhost:8000", "http://localhost:3000"])
    session_manager.init_app(app)
    
    # Import models to register schema metadata
    from task_management import models
    
    with app.app_context():
        db.create_all()

    # Register Blueprints
    from task_management.routes.auth import auth_bp
    from task_management.routes.departments import departments_bp
    from task_management.routes.employees import employees_bp
    from task_management.routes.tasks import tasks_bp
    from task_management.routes.assignments import assignments_bp
    from task_management.routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(departments_bp, url_prefix='/api')
    app.register_blueprint(employees_bp, url_prefix='/api')
    app.register_blueprint(tasks_bp, url_prefix='/api')
    app.register_blueprint(assignments_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    
    # Base route to check API status
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "message": "Task Management API is running",
            "database": app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0] # Redact credentials
        }), 200

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "An internal server error occurred"}), 500
        
    return app
