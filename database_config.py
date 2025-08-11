"""
Database Configuration for Centralized PostgreSQL
This file contains the connection configuration for the centralized database.
"""

import os
from typing import Optional

# Database Configuration for Centralized PostgreSQL
DATABASE_URL = "postgresql://postgres:development_password@localhost:5432/investment_tracker"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "investment_tracker"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "development_password"

# Application Configuration
ENVIRONMENT = "development"
DEBUG = True
LOG_LEVEL = "INFO"

# Database Connection Pool Settings
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 3600

def get_database_url() -> str:
    """Get the database connection URL."""
    return DATABASE_URL

def get_database_config() -> dict:
    """Get database configuration as a dictionary."""
    return {
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
        "database": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "pool_size": DB_POOL_SIZE,
        "max_overflow": DB_MAX_OVERFLOW,
        "pool_timeout": DB_POOL_TIMEOUT,
        "pool_recycle": DB_POOL_RECYCLE,
    }

def get_connection_string() -> str:
    """Get a formatted connection string for display purposes."""
    return f"postgresql://{POSTGRES_USER}:***@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
