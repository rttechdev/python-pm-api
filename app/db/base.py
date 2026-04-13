"""
SQLAlchemy base class for database models.

This module defines the base class that all database models inherit from.
It provides the foundation for SQLAlchemy ORM functionality.
"""

from sqlalchemy.orm import declarative_base

# Create the base class for all database models
# All model classes will inherit from this Base class
Base = declarative_base()