import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'enterprise_super_secret_key_12345')
    
    # Database Configuration
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME')
    
    # If DB variables are provided, construct MySQL URI, else fallback to SQLite
    if DB_USER and DB_NAME:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Resolve path to backend folder
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(backend_dir, 'task_manager.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'flask_sessions')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Debug/Testing flags
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False

# Mapping of environment name to config class
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
