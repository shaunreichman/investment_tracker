"""
Shared base module.

This module contains the SQLAlchemy Base class and other shared database components.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create the SQLAlchemy Base class
Base = declarative_base() 