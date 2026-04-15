"""
User database model.

This module defines the User model that represents users in the database.
It uses SQLAlchemy ORM to map Python objects to database tables.
"""

from sqlalchemy import Column, Integer, String
from app.db.base import Base

class User(Base):
    """
    User database model.

    Represents a user account in the system with authentication capabilities.

    Attributes:
        id: Unique identifier for the user (auto-generated)
        name: User's full name
        email: User's email address (must be unique)
        password: Hashed password for authentication
    """
    __tablename__ = "users"

    # Primary key - auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)

    # User's full name
    name = Column(String)

    # User's email - must be unique and indexed for fast lookups
    email = Column(String, unique=True, index=True)

    # Hashed password for secure authentication
    password = Column(String)