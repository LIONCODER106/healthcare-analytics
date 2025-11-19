"""
Configuration Management for Healthcare Analyzer
Supports multiple database types and deployment environments
"""
import os
from typing import Optional

class Config:
    """Application configuration that works across different hosting environments"""
    
    # Database Configuration
    # Priority: 1. Environment variable, 2. MySQL default, 3. SQLite fallback
    DATABASE_TYPE = os.getenv('DB_TYPE', 'mysql')  # 'mysql', 'postgresql', or 'sqlite'
    
    # MySQL Configuration (for cPanel)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'healthcare_db')
    MYSQL_USER = os.getenv('MYSQL_USER', 'healthcare_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    
    # PostgreSQL Configuration (for cloud hosting)
    POSTGRESQL_URL = os.getenv('DATABASE_URL', None)
    
    # SQLite Configuration (for local testing)
    SQLITE_PATH = os.getenv('SQLITE_PATH', 'healthcare.db')
    
    # Application Settings
    APP_NAME = "Home Healthcare Analytics"
    APP_VERSION = "1.0.0"
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production-2025')
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 8501))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # File Upload Settings
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', 200))
    ALLOWED_EXTENSIONS = {'.xlsx', '.xlsm', '.xls', '.csv'}
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', 120))
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Generate database URL based on configuration
        Returns connection string for SQLAlchemy
        """
        db_type = cls.DATABASE_TYPE.lower()
        
        if db_type == 'mysql':
            # MySQL connection for cPanel
            if not cls.MYSQL_PASSWORD:
                raise ValueError("MYSQL_PASSWORD environment variable is required for MySQL")
            return (
                f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}"
                f"@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"
                f"?charset=utf8mb4"
            )
        
        elif db_type == 'postgresql':
            # PostgreSQL connection for cloud hosting
            if cls.POSTGRESQL_URL:
                # Handle Replit/Heroku style URLs
                url = cls.POSTGRESQL_URL
                if url.startswith('postgres://'):
                    url = url.replace('postgres://', 'postgresql://', 1)
                return url
            raise ValueError("DATABASE_URL environment variable is required for PostgreSQL")
        
        elif db_type == 'sqlite':
            # SQLite for local development
            return f"sqlite:///{cls.SQLITE_PATH}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration and return any errors
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check database configuration
        try:
            cls.get_database_url()
        except ValueError as e:
            errors.append(f"Database configuration error: {e}")
        
        # Check required settings
        if cls.SECRET_KEY == 'change-this-in-production-2025':
            errors.append("WARNING: Using default SECRET_KEY. Change this in production!")
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def print_config_info(cls):
        """Print current configuration (for debugging)"""
        print("=" * 60)
        print(f"Healthcare Analytics Configuration")
        print("=" * 60)
        print(f"Database Type: {cls.DATABASE_TYPE}")
        print(f"Port: {cls.PORT}")
        print(f"Host: {cls.HOST}")
        print(f"Max Upload Size: {cls.MAX_UPLOAD_SIZE_MB}MB")
        
        if cls.DATABASE_TYPE == 'mysql':
            print(f"MySQL Host: {cls.MYSQL_HOST}:{cls.MYSQL_PORT}")
            print(f"MySQL Database: {cls.MYSQL_DATABASE}")
            print(f"MySQL User: {cls.MYSQL_USER}")
        elif cls.DATABASE_TYPE == 'postgresql':
            print(f"PostgreSQL: Configured via DATABASE_URL")
        else:
            print(f"SQLite Path: {cls.SQLITE_PATH}")
        
        is_valid, errors = cls.validate_config()
        if not is_valid:
            print("\n⚠️  Configuration Warnings/Errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\n✅ Configuration is valid")
        print("=" * 60)


class DeploymentConfig:
    """Deployment-specific configurations"""
    
    # cPanel Deployment
    CPANEL_PYTHON_PATH = "/usr/bin/python3"
    CPANEL_APP_PATH = "/home/username/public_html/healthcare"
    
    # VPS/Cloud Deployment
    USE_HTTPS = os.getenv('USE_HTTPS', 'False').lower() == 'true'
    DOMAIN_NAME = os.getenv('DOMAIN_NAME', 'localhost')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'healthcare_app.log')
    
    # Performance
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'True').lower() == 'true'
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', 300))


if __name__ == "__main__":
    # Test configuration
    Config.print_config_info()
