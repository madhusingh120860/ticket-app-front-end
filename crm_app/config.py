import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    # Core flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', "dev-secret-key")

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(PROJECT_ROOT, 'instance', 'app.db')}",
    )
    
    # Disable SQLAlchemy event system to save resources(performance optimization)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Enable SQLAlchemy echo to print all SQL statements
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() in ['true', '1', 't']

    # Set POOL_SIZE to control the number of connections in the pool, especially for production environments
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE', 5))   

    # Set POOL_TIMEOUT to avoid sqlite database connection timeout issues, especially in long-running applications
    SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', 30))  # seconds

    # Set POOL_RECYCLE to recycling Connections periodically to avoid stale connections, especially in long-running applications
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 200))  # seconds

    # Enable SQLAlchemy pool pre-ping to check if connections are alive before using them   
    SQLALCHEMY_POOL_PRE_PING = os.environ.get('SQLALCHEMY_POOL_PRE_PING', 'True').lower() in ['true', '1', 't']


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Enable SQLAlchemy echo for development

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False  # Disable SQLAlchemy echo for production

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = False  # Disable SQLAlchemy echo for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for testing



