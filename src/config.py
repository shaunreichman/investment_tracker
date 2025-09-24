"""
Configuration management for the investment tracker application.
This module handles database connection configuration for the centralized PostgreSQL database.
"""

import os


class DatabaseConfig:
    """Database configuration settings."""
    
    # Default PostgreSQL connection settings
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 5432
    DEFAULT_DB = "investment_tracker"
    DEFAULT_USER = "postgres"
    DEFAULT_PASSWORD = "development_password"
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the database connection URL from environment or use defaults."""
        # Try to get from environment first
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        
        # Fall back to individual environment variables
        host = os.getenv("POSTGRES_HOST", cls.DEFAULT_HOST)
        port = os.getenv("POSTGRES_PORT", cls.DEFAULT_PORT)
        db = os.getenv("POSTGRES_DB", cls.DEFAULT_DB)
        user = os.getenv("POSTGRES_USER", cls.DEFAULT_USER)
        password = os.getenv("POSTGRES_PASSWORD", cls.DEFAULT_PASSWORD)
        
        # Use standard PostgreSQL dialect with public schema
        return f"postgresql://{user}:{password}@{host}:{port}/{db}?options=-csearch_path%3Dpublic"
    
    @classmethod
    def get_postgres_config(cls) -> dict:
        """Get PostgreSQL connection configuration as a dictionary."""
        return {
            "host": os.getenv("POSTGRES_HOST", cls.DEFAULT_HOST),
            "port": int(os.getenv("POSTGRES_PORT", cls.DEFAULT_PORT)),
            "database": os.getenv("POSTGRES_DB", cls.DEFAULT_DB),
            "user": os.getenv("POSTGRES_USER", cls.DEFAULT_USER),
            "password": os.getenv("POSTGRES_PASSWORD", cls.DEFAULT_PASSWORD),
        }


class AppConfig:
    """Application configuration settings."""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001")
    REACT_APP_API_BASE_URL = os.getenv("REACT_APP_API_BASE_URL", "http://localhost:5001")
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return cls.ENVIRONMENT.lower() == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.ENVIRONMENT.lower() == "production"


# Convenience functions
def get_database_url() -> str:
    """Get the database connection URL."""
    return DatabaseConfig.get_database_url()


def get_postgres_config() -> dict:
    """Get PostgreSQL connection configuration."""
    return DatabaseConfig.get_postgres_config()


def is_development() -> bool:
    """Check if running in development mode."""
    return AppConfig.is_development()


def is_production() -> bool:
    """Check if running in production mode."""
    return AppConfig.is_production()
